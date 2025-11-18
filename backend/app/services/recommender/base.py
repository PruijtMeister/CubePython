"""
Base Recommender class for cube recommendation systems.

This module provides an abstract base class for implementing cube recommendation
algorithms. Subclasses must implement the fit and recommend methods.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
import pickle

from app.models.cube import CubeModel


class Recommender(ABC):
    """
    Abstract base class for cube recommendation systems.

    This class defines the interface that all recommender implementations must follow.
    It provides standardized methods for training (fit), making recommendations (recommend),
    and persisting models to disk (save/load).

    Attributes:
        is_fitted: Boolean indicating whether the recommender has been trained
        model_data: Dictionary to store any model-specific data after fitting
    """

    def __init__(self) -> None:
        """Initialize the recommender with default state."""
        self.is_fitted: bool = False
        self.model_data: Dict[str, Any] = {}

    @abstractmethod
    def fit(self, cubes: List[CubeModel]) -> "Recommender":
        """
        Train the recommender on a list of cube models.

        This method should analyze the provided cubes and build an internal
        representation that can be used to make recommendations. After successful
        completion, is_fitted should be set to True.

        Args:
            cubes: List of CubeModel instances to train on

        Returns:
            Self, to allow method chaining

        Raises:
            ValueError: If cubes list is empty or invalid
        """
        pass

    @abstractmethod
    def recommend(
        self,
        cube: CubeModel,
        n_recommendations: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate card recommendations for a given cube.

        This method should use the fitted model to suggest cards that would be
        good additions to the provided cube. Recommendations should be returned
        in order of relevance (most recommended first).

        Args:
            cube: The CubeModel to generate recommendations for
            n_recommendations: Number of recommendations to return (default: 10)
            filters: Optional filters to apply (e.g., color, type, cmc constraints)

        Returns:
            List of dictionaries containing recommended cards with scores.
            Each dictionary should contain at least:
            - 'card': Card data (dict or CardModel)
            - 'score': Recommendation score (float)
            - 'reason': Optional explanation for the recommendation (str)

        Raises:
            RuntimeError: If recommender has not been fitted yet
            ValueError: If cube is invalid or n_recommendations is non-positive
        """
        pass

    def save(self, filepath: Path | str) -> None:
        """
        Save the fitted recommender model to disk using pickle.

        Args:
            filepath: Path where the model should be saved

        Raises:
            RuntimeError: If recommender has not been fitted yet
            IOError: If unable to write to the specified filepath
        """
        if not self.is_fitted:
            raise RuntimeError(
                "Cannot save a recommender that has not been fitted. "
                "Call fit() before saving."
            )

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, filepath: Path | str) -> "Recommender":
        """
        Load a fitted recommender model from disk.

        Args:
            filepath: Path to the saved model file

        Returns:
            A fitted Recommender instance

        Raises:
            FileNotFoundError: If the specified file does not exist
            IOError: If unable to read from the specified filepath
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")

        with open(filepath, 'rb') as f:
            instance = pickle.load(f)

        return instance
