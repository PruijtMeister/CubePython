# Technical documentation

## Development Environment

This project uses [UV](https://github.com/astral-sh/uv), a fast Python package manager, to manage the virtual environment and all Python dependencies.

- **Virtual environment** (`.venv/`) - Single shared environment containing all dependencies

**Package management:**
- Dependencies are managed via `pyproject.toml` in the project root
- UV provides fast dependency resolution and installation
- Virtual environment is created using `uv venv` and dependencies installed with `uv sync`

**Setup script:**
- `setup.sh` - Automated setup for the virtual environment using UV

Virtual environment is excluded from version control via `.gitignore`.

## Folder Structure

The project is organized into three main components:

### `/scripts`
Contains data collection and processing scripts.

- **`/scripts/scrapers`** - Web scraping scripts for CubeCobra data
- **`/scripts/data_processing`** - Data transformation and cleaning scripts

#### Dependencies
- **beautifulsoup4** - HTML parsing for web scraping
- **requests** - HTTP library for API calls
- **selenium** - Web browser automation for dynamic content
- **httpx** - Async HTTP client
- **python-dotenv** - Environment variable management

### `/backend`
FastAPI application serving the recommender engine.

- **`/backend/app`** - Main application code
  - **`/backend/app/models`** - SQLModel database models
  - **`/backend/app/api`** - API route handlers
  - **`/backend/app/core`** - Core configuration (database, settings)
  - **`/backend/app/services`** - Business logic and services
- **`/backend/tests`** - Backend test suite
- **`/backend/run.py`** - Development server script

#### Technology Stack
- **FastAPI** - Modern async web framework
- **SQLModel** - SQL database ORM based on Pydantic and SQLAlchemy
- **Uvicorn** - ASGI server for running FastAPI
- **Pydantic** - Data validation using Python type annotations
- **SQLite** - Lightweight database for local storage
- **httpx** - Async HTTP client for external API calls

#### Key Features
- **Async/await support** - Built on ASGI for high-performance async operations
- **Automatic API documentation** - Interactive docs at `/docs` (Swagger UI) and `/redoc`
- **Type safety** - Full type hints with Pydantic validation
- **CORS middleware** - Pre-configured for frontend integration
- **Database migrations** - Automatic table creation via SQLModel on startup
- **Health checks** - `/api/v1/health` endpoint for monitoring
- **CardDatabase initialization** - Automatically instantiated on application startup and stored in `app.state.card_db`

#### Data Services

**CardDatabase** (`/backend/app/services/card_database.py`)
- Manages Scryfall Oracle Cards bulk data
- Automatically downloads Oracle Cards dataset on first instantiation
- Provides in-memory access to comprehensive card data
- Uses Scryfall's Bulk Data API for efficient data fetching
- Includes helper methods for searching cards by name, Oracle ID, or text query
- Data is cached locally in `backend/data/cards/oracle-cards.json`
- Dataset updates available every 12 hours from Scryfall
- Automatic version checking: compares local data version with Scryfall's latest
- Auto-updates local data when newer version is available
- Version tracking stored in `backend/data/cards/version.txt`

Usage:
```python
from backend.app.services.card_database import CardDatabase

# Initialize database (downloads if needed)
db = await CardDatabase.create()

# Search for cards
lightning_bolt = db.get_card_by_name("Lightning Bolt")
results = db.search_cards("bolt", limit=10)
```

**CubeDatabase** (`/backend/app/services/cube_database.py`)
- Manages CubeCobra cube data with local caching
- Fetches cube data by cube ID from CubeCobra
- Stores each cube as a separate JSON file in local cache
- Provides in-memory caching for frequently accessed cubes
- Automatically downloads cube data on first request
- Data is cached locally in `backend/data/cubes/{cube_id}.json`
- Includes placeholder `fetch_cube` function for CubeCobra integration

Usage:
```python
from backend.app.services.cube_database import CubeDatabase

# Initialize database
db = CubeDatabase()

# Get cube by ID (fetches and caches if not already local)
cube_data = await db.get_cube("1fdv1")

# Check if cube is cached
is_cached = db.is_cube_cached("1fdv1")

# Get list of all cached cubes
cached_ids = db.get_cached_cube_ids()
```

**Recommender** (`/backend/app/services/recommender/base.py`)
- Abstract base class for cube recommendation systems
- Defines standard interface for all recommendation implementations
- Provides fit/recommend pattern for training and inference
- Includes save/load methods for model persistence using pickle
- Subclasses must implement `fit()` and `recommend()` methods

Key methods:
- `fit(cubes: List[CubeModel])` - Train the recommender on cube data
- `recommend(cube: CubeModel, n_recommendations: int, filters: Optional[Dict])` - Generate card recommendations
- `save(filepath: Path | str)` - Persist fitted model to disk
- `load(filepath: Path | str)` - Load fitted model from disk

Usage:
```python
from backend.app.services.recommender import Recommender
from backend.app.models.cube import CubeModel

# Subclass must implement abstract methods
class MyRecommender(Recommender):
    def fit(self, cubes: List[CubeModel]) -> "MyRecommender":
        # Train on cube data
        self.model_data['num_cubes'] = len(cubes)
        self.is_fitted = True
        return self

    def recommend(self, cube: CubeModel, n_recommendations: int = 10,
                  filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.is_fitted:
            raise RuntimeError("Model not fitted")
        # Generate recommendations
        return [{'card': {...}, 'score': 0.95, 'reason': '...'}]

# Train and use recommender
recommender = MyRecommender()
recommender.fit(training_cubes)

# Make recommendations
recommendations = recommender.recommend(target_cube, n_recommendations=5)

# Save and load
recommender.save("models/my_recommender.pkl")
loaded_recommender = MyRecommender.load("models/my_recommender.pkl")
```

**CollaborativeFilteringRecommender** (`/backend/app/services/recommender/collaborative_filtering.py`)
- Cube-cube collaborative filtering implementation
- Finds cubes similar to target cube based on shared cards
- Recommends cards appearing in similar cubes but not in target cube
- Uses Jaccard similarity coefficient for cube-cube similarity
- Scores recommendations based on appearance frequency weighted by similarity

Algorithm overview:
1. During `fit()`: Builds indices of which cards appear in which cubes
2. During `recommend()`:
   - Finds top N most similar cubes to the target cube
   - Identifies candidate cards from similar cubes
   - Scores cards by weighted appearance frequency
   - Returns top recommendations with explanations

Key features:
- Extracts card IDs using `oracle_id` (preferred) or `name` (fallback)
- Normalizes recommendation scores for consistency
- Provides explanatory reasons for each recommendation
- Efficient similarity calculation using set operations

Usage:
```python
from backend.app.services.recommender import CollaborativeFilteringRecommender
from backend.app.models.cube import CubeModel

# Initialize and train
recommender = CollaborativeFilteringRecommender()
recommender.fit(training_cubes)  # List[CubeModel]

# Generate recommendations for a target cube
recommendations = recommender.recommend(
    cube=target_cube,
    n_recommendations=10
)

# Each recommendation contains:
# - 'card_id': Card identifier (oracle_id or name)
# - 'card_name': Human-readable card name
# - 'score': Normalized recommendation score (0.0 to 1.0)
# - 'reason': Explanation (e.g., "Appears in 15/50 similar cubes")

# Save and load trained model
recommender.save("models/collaborative_filtering.pkl")
loaded = CollaborativeFilteringRecommender.load("models/collaborative_filtering.pkl")
```

#### API Routes

**Cards API** (`/backend/app/api/cards.py`)
- Provides endpoints for accessing card data from the CardDatabase
- All routes are prefixed with `/api/v1/cards`
- CardDatabase is accessed via `request.app.state.card_db`

Available endpoints:
- `GET /api/v1/cards/{card_id}` - Get a card by its Scryfall ID
- `GET /api/v1/cards/name/{card_name}` - Get a card by its exact name
- `GET /api/v1/cards/search/{query}?limit=10` - Search for cards by name (case-insensitive partial match)

Example usage:
```bash
# Get card by ID
curl "http://localhost:8000/api/v1/cards/77c6fa74-5543-42ac-9ead-0e890b188e99"

# Get card by exact name
curl "http://localhost:8000/api/v1/cards/name/Lightning%20Bolt"

# Search for cards
curl "http://localhost:8000/api/v1/cards/search/lightning?limit=5"
```

Response format:
- Returns card data as JSON directly from the Scryfall Oracle Cards dataset
- Each card contains comprehensive information including name, mana cost, type, oracle text, colors, legalities, and more
- Error responses follow standard HTTP status codes (404 for not found, etc.)

**Cubes API** (`/backend/app/api/cubes.py`)
- Provides endpoints for accessing cube data from the CubeDatabase
- All routes are prefixed with `/api/v1/cubes`
- CubeDatabase is accessed via `request.app.state.cube_db`
- CubeDatabase is automatically instantiated on application startup

Available endpoints:
- `GET /api/v1/cubes/` - Get a list of all cached cube identifiers
- `GET /api/v1/cubes/{cube_id}` - Get a cube by its CubeCobra identifier

Example usage:
```bash
# Get all cached cube identifiers
curl "http://localhost:8000/api/v1/cubes/"

# Get cube by ID
curl "http://localhost:8000/api/v1/cubes/1fdv1"
```

Response format:
- `GET /api/v1/cubes/` returns an array of cube ID strings
- `GET /api/v1/cubes/{cube_id}` returns full cube data as JSON including:
  - `id`: CubeCobra unique cube ID
  - `name`: Cube name
  - `owner`: Cube owner username
  - `description`: Cube description
  - `card_count`: Number of cards in the cube
  - `cards`: List of cards in the cube
  - `tags`: Cube tags
  - And additional metadata fields
- Returns 404 if cube is not cached and cannot be fetched
- Returns 500 if there's an error loading or fetching the cube

Notes:
- If a cube is not in the local cache and the CubeCobra fetch implementation is not available, the endpoint will return a 404 with a helpful error message
- Cubes are cached locally in `backend/data/cubes/{cube_id}.json` for fast subsequent access

### `/frontend`
React with TypeScript UI for inspecting data and recommendations.

Built with Create React App (TypeScript template) for rapid development and built-in tooling.

- **`/frontend/src`** - Source code
  - **`/frontend/src/components`** - Reusable React components
  - **`/frontend/src/pages`** - Page components
  - **`/frontend/src/services`** - API client and service layer
  - **`/frontend/src/types`** - TypeScript type definitions
- **`/frontend/public`** - Static assets
- **`/frontend/build`** - Production build output (generated)

#### Technology Stack
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Create React App** - Build tooling and development server
- **React Scripts** - Build and development scripts