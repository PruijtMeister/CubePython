"""
API routes for cube-related endpoints.
"""

from fastapi import APIRouter, HTTPException, Request

from app.models.cube import CubeModel

router = APIRouter()


@router.get("/", response_model=list[str])
async def get_all_cube_identifiers(request: Request) -> list[str]:
    """
    Get a list of all cube identifiers in the database.

    Returns:
        List of all cube IDs available

    Example:
        GET /api/v1/cubes/
        Response: ["1fdv1", "5h3k2", "abcde"]
    """
    cube_db = request.app.state.cube_db
    return cube_db.get_all_cube_ids()


@router.get("/search/{query}", response_model=list[dict[str, Any]])
async def search_cubes(query: str, request: Request, limit: int = 10) -> list[dict[str, Any]]:
    """
    Search for cubes by name.

    Args:
        query: Search query string
        limit: Maximum number of results (default: 10)

    Returns:
        List of cubes matching the query

    Example:
        GET /api/v1/cubes/search/vintage?limit=5
    """
    cube_db = request.app.state.cube_db
    return cube_db.search_cubes(query, limit)


@router.get("/stats/count")
async def get_cube_count(request: Request) -> dict[str, int]:
    """
    Get the total number of cubes in the database.

    Returns:
        Dictionary with the count

    Example:
        GET /api/v1/cubes/stats/count
        Response: {"count": 12345}
    """
    cube_db = request.app.state.cube_db
    return {"count": cube_db.get_cube_count()}


@router.get("/{cube_id}")
async def get_cube_by_id(cube_id: str, request: Request) -> CubeModel:
    """
    Get a cube by its CubeCobra identifier.

    Args:
        cube_id: The CubeCobra cube ID (e.g., "1fdv1")

    Returns:
        Cube data model containing all cube information

    Raises:
        HTTPException: 404 if cube not found

    Example:
        GET /api/v1/cubes/1fdv1
        Response: {
            "shortId": "1fdv1",
            "name": "My Cube",
            "cardCount": 360,
            ...
        }
    """
    cube_db = request.app.state.cube_db
    cube_data = cube_db.get_cube(cube_id)

    if cube_data is None:
    try:
        cube_data = await cube_db.get_cube(cube_id)
        return CubeModel.model_validate(cube_data)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Cube with ID '{cube_id}' not found"
        )

    return cube_data
