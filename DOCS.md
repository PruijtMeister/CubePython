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