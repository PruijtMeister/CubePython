"""
API routes for recommender-related endpoints.
"""

from fastapi import APIRouter, HTTPException, Request

from app.models.recommender import (
    CubeBasedCollaborativeFilteringConfig,
    RecommenderAlgorithmInfo,
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.recommender import CubeBasedCollaborativeFilteringRecommender

router = APIRouter()


def get_available_algorithms() -> list[RecommenderAlgorithmInfo]:
    """
    Get metadata for all available recommender algorithms.

    Returns:
        List of algorithm information including schemas and defaults
    """
    # Get the JSON schema for CubeBasedCollaborativeFilteringConfig
    cube_based_schema = CubeBasedCollaborativeFilteringConfig.model_json_schema()
    cube_based_default = CubeBasedCollaborativeFilteringConfig()

    algorithms = [
        RecommenderAlgorithmInfo(
            type="cube_based_collaborative_filtering",
            name="Cube-Based Collaborative Filtering",
            description=(
                "Finds cubes similar to yours based on card overlap, then recommends "
                "cards that appear frequently in those similar cubes. Ideal for "
                "discovering cards that fit your cube's overall strategy and power level."
            ),
            default_config=cube_based_default.model_dump(),
            config_schema=cube_based_schema,
            is_default=True,
        )
    ]

    return algorithms


@router.get("/algorithms", response_model=list[RecommenderAlgorithmInfo])
async def list_algorithms() -> list[RecommenderAlgorithmInfo]:
    """
    Get a list of all available recommender algorithms with their configurations.

    Returns detailed information about each algorithm including:
    - Algorithm type and name
    - Description of how it works
    - Default configuration parameters
    - JSON schema for configuration (for dynamic UI generation)
    - Whether it's the default algorithm

    This endpoint is designed to support dynamic UI generation, where the frontend
    can use the config_schema to build forms for users to customize algorithm parameters.

    Example:
        GET /api/v1/recommenders/algorithms
        Response: [
            {
                "type": "cube_based_collaborative_filtering",
                "name": "Cube-Based Collaborative Filtering",
                "description": "Finds cubes similar to yours...",
                "default_config": {...},
                "config_schema": {...},
                "is_default": true
            }
        ]
    """
    return get_available_algorithms()


@router.post("/recommend", response_model=RecommendationResponse)
async def generate_recommendations(
    request_body: RecommendationRequest,
    request: Request,
) -> RecommendationResponse:
    """
    Generate card recommendations for a cube using a specified algorithm.

    This endpoint allows you to:
    1. Specify which cube to analyze
    2. Choose which recommendation algorithm to use
    3. Customize algorithm parameters (e.g., similarity thresholds)
    4. Control how many recommendations to receive

    The algorithm will analyze the cube and return a ranked list of card
    recommendations with scores and explanations.

    Args:
        request_body: Recommendation request containing cube_id, algorithm config, and n_recommendations
        request: FastAPI request object for accessing app state

    Returns:
        Recommendation response with ranked card suggestions

    Raises:
        HTTPException: 404 if cube not found
        HTTPException: 500 if there's an error during recommendation

    Example:
        POST /api/v1/recommenders/recommend
        {
            "cube_id": "1fdv1",
            "algorithm_config": {
                "type": "cube_based_collaborative_filtering",
                "n_similar_cubes": 100,
                "min_similarity": 0.1
            },
            "n_recommendations": 20
        }
    """
    cube_db = request.app.state.cube_db

    try:
        # Fetch the cube data
        cube_data = await cube_db.get_cube(request_body.cube_id)

        # Validate cube data
        from app.models.cube import CubeModel
        cube = CubeModel.model_validate(cube_data)

        # Create recommender based on algorithm type
        algorithm_config = request_body.algorithm_config

        if algorithm_config.type == "cube_based_collaborative_filtering":
            recommender = CubeBasedCollaborativeFilteringRecommender(
                config=algorithm_config
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown algorithm type: {algorithm_config.type}",
            )

        # Check if we have a fitted recommender in app state
        # For now, we'll need to fit on-demand (in production, you'd cache fitted models)
        if not hasattr(request.app.state, "fitted_recommenders"):
            request.app.state.fitted_recommenders = {}

        # Get all cached cubes for training
        cached_cube_ids = cube_db.get_cached_cube_ids()

        if not cached_cube_ids:
            raise HTTPException(
                status_code=400,
                detail="No cubes available for training. Please ensure at least some cubes are cached.",
            )

        # Load all cached cubes for fitting
        training_cubes = []
        for cube_id in cached_cube_ids:
            try:
                cube_data_train = await cube_db.get_cube(cube_id)
                training_cubes.append(CubeModel.model_validate(cube_data_train))
            except Exception:
                # Skip cubes that fail to load
                continue

        if not training_cubes:
            raise HTTPException(
                status_code=500,
                detail="Failed to load training cubes",
            )

        # Fit the recommender
        recommender.fit(training_cubes)

        # Generate recommendations
        recommendations = recommender.recommend(
            cube=cube,
            n_recommendations=request_body.n_recommendations,
        )

        return RecommendationResponse(
            cube_id=request_body.cube_id,
            algorithm_type=algorithm_config.type,
            recommendations=recommendations,
            n_recommendations=len(recommendations),
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Cube with ID '{request_body.cube_id}' not found",
        )
    except NotImplementedError:
        raise HTTPException(
            status_code=404,
            detail=f"Cube with ID '{request_body.cube_id}' not found in cache",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}",
        )
