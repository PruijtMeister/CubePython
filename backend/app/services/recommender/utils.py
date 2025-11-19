"""
Utility functions for recommender systems.

This module provides helper functions for building and manipulating
data structures used in collaborative filtering and other recommendation
algorithms.
"""

from typing import List, Tuple, Dict, Literal
from collections import defaultdict
from scipy.sparse import csr_matrix, diags
import numpy as np

from app.models.cube import CubeModel

SimilarityMetric = Literal["cosine", "jaccard"]


def generate_sparse_cf_matrix(
    cubes: List[CubeModel],
    binary: bool = True
) -> Tuple[csr_matrix, Dict[int, int], Dict[str, int]]:
    """
    Generate a sparse matrix for collaborative filtering from cube data.

    Creates a sparse cube-card matrix where rows represent cubes and columns
    represent unique cards across all cubes. This matrix can be used for
    collaborative filtering algorithms, similarity calculations, and other
    recommendation tasks.

    Args:
        cubes: List of CubeModel instances to build the matrix from
        binary: If True, duplicate cards are represented as 1. If False,
                represents the actual count of each card in the cube.

    Returns:
        A tuple containing:
        - csr_matrix: Sparse matrix of shape (n_cubes, n_unique_cards)
        - Dict[int, int]: Mapping from card_id to column index in the matrix
        - Dict[str, int]: Mapping from cube_id to row index in the matrix

    Raises:
        ValueError: If cubes list is empty

    Examples:
        >>> from app.models.cube import CubeModel
        >>> from app.services.recommender.utils import generate_sparse_cf_matrix
        >>>
        >>> # Create sparse matrix with binary values (1 for presence)
        >>> matrix, card_to_col, cube_to_row = generate_sparse_cf_matrix(
        ...     cubes, binary=True
        ... )
        >>>
        >>> # Create sparse matrix with counts
        >>> matrix, card_to_col, cube_to_row = generate_sparse_cf_matrix(
        ...     cubes, binary=False
        ... )
        >>>
        >>> # Access the matrix
        >>> print(f"Matrix shape: {matrix.shape}")
        >>> print(f"Number of cubes: {len(cube_to_row)}")
        >>> print(f"Number of unique cards: {len(card_to_col)}")
    """
    if not cubes:
        raise ValueError("Cannot generate matrix from empty cube list")

    # Build mappings
    cube_to_row: Dict[str, int] = {}
    card_to_col: Dict[int, int] = {}
    card_counts: Dict[Tuple[int, int], int] = defaultdict(int)

    # First pass: build cube and card indices
    for cube_idx, cube in enumerate(cubes):
        cube_to_row[cube.id] = cube_idx

        # Count cards in this cube
        for card_id in cube.card_ids:
            # Add card to column mapping if not already present
            if card_id not in card_to_col:
                card_to_col[card_id] = len(card_to_col)

            # Track card counts for this cube
            col_idx = card_to_col[card_id]
            card_counts[(cube_idx, col_idx)] += 1

    # Build sparse matrix in COO format (coordinate format)
    # then convert to CSR for efficient operations
    n_cubes = len(cubes)
    n_cards = len(card_to_col)

    # Prepare data for sparse matrix construction
    rows = []
    cols = []
    data = []

    for (cube_idx, card_idx), count in card_counts.items():
        rows.append(cube_idx)
        cols.append(card_idx)
        data.append(1 if binary else count)

    # Create sparse matrix
    matrix = csr_matrix(
        (data, (rows, cols)),
        shape=(n_cubes, n_cards),
        dtype=np.int32
    )

    return matrix, card_to_col, cube_to_row


def calculate_card_cooccurrence(cube_card_matrix: csr_matrix) -> csr_matrix:
    """
    Calculate card co-occurrence matrix from cube-card matrix.

    Computes how often pairs of cards appear together across cubes.
    The resulting matrix is symmetric, where cell (i,j) represents
    the number of cubes that contain both card i and card j.

    Args:
        cube_card_matrix: Sparse matrix of shape (n_cubes, n_cards)
                         where rows are cubes and columns are cards

    Returns:
        csr_matrix: Symmetric co-occurrence matrix of shape (n_cards, n_cards)
                   where each cell (i,j) is the count of cubes containing
                   both card i and card j

    Examples:
        >>> # Generate cube-card matrix
        >>> matrix, card_to_col, cube_to_row = generate_sparse_cf_matrix(cubes)
        >>>
        >>> # Calculate co-occurrence
        >>> cooccurrence = calculate_card_cooccurrence(matrix)
        >>>
        >>> # Get co-occurrence count for two cards
        >>> card_i_col = card_to_col[card_i_id]
        >>> card_j_col = card_to_col[card_j_id]
        >>> count = cooccurrence[card_i_col, card_j_col]
        >>> print(f"Cards appear together in {count} cubes")
    """
    # M^T @ M gives us card-card co-occurrence matrix
    # where (i,j) = number of cubes containing both card i and j
    cooccurrence = cube_card_matrix.T @ cube_card_matrix

    return cooccurrence.tocsr()


def calculate_card_similarities(
    cooccurrence_matrix: csr_matrix,
    metric: SimilarityMetric = "cosine"
) -> csr_matrix:
    """
    Calculate pairwise card similarities from co-occurrence matrix.

    Converts raw co-occurrence counts into normalized similarity scores
    using various similarity metrics. The resulting matrix contains
    similarity scores between 0 and 1.

    Args:
        cooccurrence_matrix: Card-card co-occurrence matrix from
                            calculate_card_cooccurrence()
        metric: Similarity metric to use:
               - "cosine": Cosine similarity (default)
               - "jaccard": Jaccard similarity coefficient

    Returns:
        csr_matrix: Similarity matrix of shape (n_cards, n_cards) with
                   values between 0 and 1, where higher values indicate
                   greater similarity

    Raises:
        ValueError: If metric is not one of the supported types

    Examples:
        >>> # Calculate co-occurrence and similarities
        >>> matrix, card_to_col, _ = generate_sparse_cf_matrix(cubes)
        >>> cooccurrence = calculate_card_cooccurrence(matrix)
        >>>
        >>> # Cosine similarity (normalized by geometric mean)
        >>> cosine_sim = calculate_card_similarities(cooccurrence, metric="cosine")
        >>>
        >>> # Jaccard similarity (intersection over union)
        >>> jaccard_sim = calculate_card_similarities(cooccurrence, metric="jaccard")
        >>>
        >>> # Find most similar cards to a given card
        >>> card_col = card_to_col[target_card_id]
        >>> similarities = cosine_sim[card_col].toarray().flatten()
        >>> top_similar_indices = np.argsort(similarities)[-10:][::-1]
    """
    if metric not in ["cosine", "jaccard"]:
        raise ValueError(f"Unsupported metric: {metric}. Use 'cosine' or 'jaccard'")

    # Get diagonal (how many cubes each card appears in)
    card_counts = cooccurrence_matrix.diagonal()

    n_cards = cooccurrence_matrix.shape[0]

    if metric == "cosine":
        # Cosine similarity: co-occurrence / sqrt(count_i * count_j)
        # Normalize by geometric mean of individual counts

        # Create diagonal matrix with 1/sqrt(count) for normalization
        # Handle zero counts to avoid division by zero
        inv_sqrt_counts = np.zeros(n_cards)
        nonzero_mask = card_counts > 0
        inv_sqrt_counts[nonzero_mask] = 1.0 / np.sqrt(card_counts[nonzero_mask])

        # Create sparse diagonal matrix for normalization
        normalizer = diags(inv_sqrt_counts, format='csr')

        # Similarity = D^-0.5 @ C @ D^-0.5
        # where D is diagonal matrix of counts, C is co-occurrence
        similarity = normalizer @ cooccurrence_matrix @ normalizer

    elif metric == "jaccard":
        # Jaccard similarity: intersection / union
        # |A ∩ B| / |A ∪ B| = cooccur(i,j) / (count(i) + count(j) - cooccur(i,j))

        # Convert to dense for easier computation (consider keeping sparse for large matrices)
        cooccur_dense = cooccurrence_matrix.toarray()

        # Create union matrix: count[i] + count[j] for all pairs
        union = card_counts[:, np.newaxis] + card_counts[np.newaxis, :]

        # Jaccard = intersection / union
        # union - intersection gives us the adjustment needed
        with np.errstate(divide='ignore', invalid='ignore'):
            similarity_dense = np.divide(
                cooccur_dense,
                union - cooccur_dense,
                where=(union - cooccur_dense) > 0
            )
            similarity_dense = np.nan_to_num(similarity_dense, 0.0)

        similarity = csr_matrix(similarity_dense)

    return similarity.tocsr()
