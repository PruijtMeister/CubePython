"""
Pydantic models for recommender algorithm configurations.

These models define the configurable parameters for different recommendation
algorithms. They are used for API requests/responses and provide JSON schemas
for dynamic UI generation.
"""

from typing import Literal, Union
from pydantic import BaseModel, Field


class CubeBasedCollaborativeFilteringConfig(BaseModel):
    """
    Configuration for Cube-Based Collaborative Filtering algorithm.

    This algorithm finds cubes similar to the target cube based on card overlap,
    then recommends cards that appear in similar cubes. The parameters control
    how similarity is calculated and which cubes are considered.
    """

    type: Literal["cube_based_collaborative_filtering"] = Field(
        default="cube_based_collaborative_filtering",
        description="Algorithm type identifier"
    )

    n_similar_cubes: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Number of similar cubes to consider when making recommendations"
    )

    min_similarity: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum similarity threshold (0.0 to 1.0). Cubes below this threshold are ignored"
    )

    similarity_metric: Literal["jaccard"] = Field(
        default="jaccard",
        description="Similarity calculation method (currently only Jaccard is supported)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "cube_based_collaborative_filtering",
                "n_similar_cubes": 50,
                "min_similarity": 0.1,
                "similarity_metric": "jaccard"
            }
        }
    }


# Union type for all algorithm configurations (discriminated by 'type' field)
RecommenderConfig = CubeBasedCollaborativeFilteringConfig


class RecommenderAlgorithmInfo(BaseModel):
    """
    Metadata about a recommender algorithm.

    This model provides information about an algorithm including its name,
    description, and JSON schema for its configuration parameters.
    """

    type: str = Field(..., description="Algorithm type identifier")
    name: str = Field(..., description="Human-readable algorithm name")
    description: str = Field(..., description="Description of how the algorithm works")
    default_config: dict = Field(..., description="Default configuration parameters")
    config_schema: dict = Field(..., description="JSON schema for configuration parameters")
    is_default: bool = Field(
        default=False,
        description="Whether this is the default algorithm"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "cube_based_collaborative_filtering",
                "name": "Cube-Based Collaborative Filtering",
                "description": "Recommends cards based on similarity to other cubes",
                "default_config": {
                    "type": "cube_based_collaborative_filtering",
                    "n_similar_cubes": 50,
                    "min_similarity": 0.0,
                    "similarity_metric": "jaccard"
                },
                "config_schema": {},
                "is_default": True
            }
        }
    }


class RecommendationRequest(BaseModel):
    """
    Request model for generating recommendations.

    Specifies which cube to generate recommendations for, which algorithm to use,
    and how many recommendations to return.
    """

    cube_id: str = Field(..., description="CubeCobra cube ID")
    algorithm_config: RecommenderConfig = Field(
        default=CubeBasedCollaborativeFilteringConfig(),
        description="Algorithm configuration (defaults to cube-based collaborative filtering)"
    )
    n_recommendations: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of recommendations to return"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "cube_id": "1fdv1",
                "algorithm_config": {
                    "type": "cube_based_collaborative_filtering",
                    "n_similar_cubes": 50,
                    "min_similarity": 0.1
                },
                "n_recommendations": 10
            }
        }
    }


class RecommendationResponse(BaseModel):
    """
    Response model for recommendations.

    Contains the list of recommended cards along with metadata about the
    recommendation process.
    """

    cube_id: str = Field(..., description="CubeCobra cube ID that was analyzed")
    algorithm_type: str = Field(..., description="Algorithm type that was used")
    recommendations: list[dict] = Field(
        ...,
        description="List of recommended cards with scores and reasons"
    )
    n_recommendations: int = Field(..., description="Number of recommendations returned")

    model_config = {
        "json_schema_extra": {
            "example": {
                "cube_id": "1fdv1",
                "algorithm_type": "cube_based_collaborative_filtering",
                "recommendations": [
                    {
                        "card_id": "b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6",
                        "card_name": "Lightning Bolt",
                        "score": 0.85,
                        "reason": "Appears in 42/50 similar cubes"
                    }
                ],
                "n_recommendations": 1
            }
        }
    }
