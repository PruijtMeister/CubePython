"""
API routes for cube-related endpoints.
"""

from fastapi import APIRouter, HTTPException, Request

from app.models.cube import CubeModel

router = APIRouter()


@router.get("/", response_model=list[str])
async def get_all_cube_identifiers(request: Request) -> list[str]:
    """
    Get a list of all cached cube identifiers.

    Returns:
        List of cube IDs that are available in the local cache

    Example:
        GET /api/v1/cubes/
        Response: ["1fdv1", "5h3k2", "abcde"]
    """
    cube_db = request.app.state.cube_db
    return cube_db.get_cached_cube_ids()


@router.get("/{cube_id}")
async def get_cube_by_id(cube_id: str, request: Request) -> CubeModel:
    """
    Get a cube by its CubeCobra identifier.

    If the cube is not cached locally, it will attempt to fetch it from
    CubeCobra (if the fetch implementation is available).

    Args:
        cube_id: The CubeCobra cube ID (e.g., "1fdv1")

    Returns:
        Cube data model containing all cube information

    Raises:
        HTTPException: 404 if cube not found or cannot be fetched
        HTTPException: 500 if there's an error loading or fetching the cube

    Example:
        GET /api/v1/cubes/1fdv1
        Response: {
            "id": "1fdv1",
            "name": "My Cube",
            "owner": "username",
            "card_count": 360,
            ...
        }
    """
    cube_db = request.app.state.cube_db

    try:
        cube_data = await cube_db.get_cube(cube_id)
        return CubeModel.model_validate(cube_data)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Cube with ID '{cube_id}' not found and could not be fetched"
        )
    except NotImplementedError:
        raise HTTPException(
            status_code=404,
            detail=f"Cube with ID '{cube_id}' not found in cache. "
                   f"Automatic fetching from CubeCobra is not yet implemented."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving cube '{cube_id}': {str(e)}"
        )
