"""Recommender module for cube recommendation systems."""

from app.services.recommender.base import Recommender
from app.services.recommender.collaborative_filtering import CollaborativeFilteringRecommender

__all__ = ["Recommender", "CollaborativeFilteringRecommender"]
