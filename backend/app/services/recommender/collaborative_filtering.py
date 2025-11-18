"""
Cube-Based Collaborative Filtering Recommender.

This module implements a collaborative filtering approach for cube recommendations
based on cube-cube similarity. It finds cubes similar to the target cube and
recommends cards that appear in those similar cubes.
"""

from typing import Any, Dict, List, Optional, Set
from collections import defaultdict
import numpy as np

from app.models.cube import CubeModel
from app.models.recommender import CubeBasedCollaborativeFilteringConfig
from app.services.recommender.base import Recommender


class CubeBasedCollaborativeFilteringRecommender(Recommender):
    """
    Cube-based collaborative filtering recommender.

    This recommender finds cubes similar to a target cube based on their shared
    cards, then recommends cards that appear in similar cubes but not in the
    target cube. Similarity is calculated using Jaccard similarity coefficient.

    The recommendation score for each card is based on:
    - How frequently it appears in similar cubes
    - The similarity scores of cubes containing the card
    - The card's popularity across all cubes (as a tiebreaker)

    Configuration parameters:
    - n_similar_cubes: Number of similar cubes to consider
    - min_similarity: Minimum similarity threshold for cubes
    - similarity_metric: Method for calculating similarity (currently only Jaccard)
    """

    def __init__(self, config: Optional[CubeBasedCollaborativeFilteringConfig] = None) -> None:
        """
        Initialize the cube-based collaborative filtering recommender.

        Args:
            config: Configuration for the recommender. If None, uses defaults.
        """
        super().__init__()
        self.config = config or CubeBasedCollaborativeFilteringConfig()
        self.cube_cards: Dict[str, Set[str]] = {}
        self.card_cubes: Dict[str, Set[str]] = defaultdict(set)
        self.card_names: Dict[str, str] = {}
        self.all_card_ids: Set[str] = set()

    def _extract_card_ids(self, cube: CubeModel) -> Set[str]:
        """
        Extract unique card IDs from a cube.

        Args:
            cube: CubeModel to extract cards from

        Returns:
            Set of card IDs (oracle_id or name as fallback)
        """
        card_ids = set()
        for card in cube.cards:
            # Use oracle_id if available, otherwise fall back to name
            card_id = card.get('oracle_id') or card.get('name')
            if card_id:
                card_ids.add(card_id)
                # Store card name for recommendations
                if 'name' in card:
                    self.card_names[card_id] = card['name']
        return card_ids

    def _calculate_jaccard_similarity(self, set1: Set[str], set2: Set[str]) -> float:
        """
        Calculate Jaccard similarity between two sets.

        Args:
            set1: First set
            set2: Second set

        Returns:
            Jaccard similarity coefficient (0.0 to 1.0)
        """
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def fit(self, cubes: List[CubeModel]) -> "CubeBasedCollaborativeFilteringRecommender":
        """
        Train the recommender on a list of cube models.

        This builds an index of which cards appear in which cubes,
        enabling efficient similarity calculations during recommendation.

        Args:
            cubes: List of CubeModel instances to train on

        Returns:
            Self, to allow method chaining

        Raises:
            ValueError: If cubes list is empty or invalid
        """
        if not cubes:
            raise ValueError("Cannot fit on empty cube list")

        # Reset state
        self.cube_cards = {}
        self.card_cubes = defaultdict(set)
        self.card_names = {}
        self.all_card_ids = set()

        # Build cube-card and card-cube indices
        for cube in cubes:
            card_ids = self._extract_card_ids(cube)
            self.cube_cards[cube.id] = card_ids
            self.all_card_ids.update(card_ids)

            # Build reverse index: card -> cubes
            for card_id in card_ids:
                self.card_cubes[card_id].add(cube.id)

        # Store metadata
        self.model_data['num_cubes'] = len(cubes)
        self.model_data['num_cards'] = len(self.all_card_ids)
        self.model_data['avg_cube_size'] = np.mean([len(cards) for cards in self.cube_cards.values()])

        self.is_fitted = True
        return self

    def _find_similar_cubes(
        self,
        target_cube_id: str,
        target_cards: Set[str],
        n_similar: Optional[int] = None,
        min_similarity: Optional[float] = None
    ) -> List[tuple[str, float]]:
        """
        Find cubes most similar to the target cube.

        Args:
            target_cube_id: ID of the target cube (to exclude from results)
            target_cards: Set of card IDs in the target cube
            n_similar: Number of similar cubes to return (uses config if not specified)
            min_similarity: Minimum similarity threshold (uses config if not specified)

        Returns:
            List of (cube_id, similarity_score) tuples, sorted by similarity descending
        """
        if n_similar is None:
            n_similar = self.config.n_similar_cubes
        if min_similarity is None:
            min_similarity = self.config.min_similarity

        similarities = []

        for cube_id, cube_cards in self.cube_cards.items():
            # Skip the target cube itself
            if cube_id == target_cube_id:
                continue

            similarity = self._calculate_jaccard_similarity(target_cards, cube_cards)

            # Only consider cubes above the minimum similarity threshold
            if similarity >= min_similarity:
                similarities.append((cube_id, similarity))

        # Sort by similarity descending and take top n
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n_similar]

    def recommend(
        self,
        cube: CubeModel,
        n_recommendations: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate card recommendations for a given cube.

        Finds cubes similar to the target cube based on card overlap,
        then recommends cards that appear in similar cubes but not in
        the target cube.

        Args:
            cube: The CubeModel to generate recommendations for
            n_recommendations: Number of recommendations to return (default: 10)
            filters: Optional filters to apply (not yet implemented)

        Returns:
            List of dictionaries containing recommended cards with scores.
            Each dictionary contains:
            - 'card_id': Card identifier (oracle_id or name)
            - 'card_name': Card name
            - 'score': Recommendation score (0.0 to 1.0)
            - 'reason': Explanation for the recommendation

        Raises:
            RuntimeError: If recommender has not been fitted yet
            ValueError: If cube is invalid or n_recommendations is non-positive
        """
        if not self.is_fitted:
            raise RuntimeError(
                "Recommender has not been fitted yet. Call fit() before recommend()."
            )

        if n_recommendations <= 0:
            raise ValueError("n_recommendations must be positive")

        # Extract cards from target cube
        target_cards = self._extract_card_ids(cube)

        if not target_cards:
            raise ValueError("Target cube has no valid cards")

        # Find similar cubes using configured parameters
        similar_cubes = self._find_similar_cubes(
            cube.id,
            target_cards
        )

        if not similar_cubes:
            # No similar cubes found, return empty recommendations
            return []

        # Calculate scores for candidate cards
        card_scores: Dict[str, float] = defaultdict(float)
        card_appearance_count: Dict[str, int] = defaultdict(int)

        total_similarity = sum(sim for _, sim in similar_cubes)

        for cube_id, similarity in similar_cubes:
            cube_card_set = self.cube_cards[cube_id]

            # Consider cards in this similar cube that are NOT in target cube
            candidate_cards = cube_card_set - target_cards

            for card_id in candidate_cards:
                # Weight by cube similarity
                card_scores[card_id] += similarity
                card_appearance_count[card_id] += 1

        # Normalize scores by total similarity
        if total_similarity > 0:
            for card_id in card_scores:
                card_scores[card_id] /= total_similarity

        # Sort by score descending
        sorted_cards = sorted(
            card_scores.items(),
            key=lambda x: (x[1], card_appearance_count[x[0]]),
            reverse=True
        )

        # Build recommendations
        recommendations = []
        for card_id, score in sorted_cards[:n_recommendations]:
            card_name = self.card_names.get(card_id, card_id)
            num_appearances = card_appearance_count[card_id]
            num_similar_cubes = len(similar_cubes)

            recommendations.append({
                'card_id': card_id,
                'card_name': card_name,
                'score': round(score, 4),
                'reason': (
                    f"Appears in {num_appearances}/{num_similar_cubes} similar cubes "
                    f"(avg similarity: {score:.2%})"
                )
            })

        return recommendations
