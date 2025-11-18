# Technical documentation

## Development Environment

This project uses [UV](https://github.com/astral-sh/uv), a fast Python package manager, to manage virtual environments and dependencies for different components:

- **Backend virtual environment** (`backend/.venv/`) - Contains FastAPI and related dependencies
- **Scripts virtual environment** (`scripts/.venv/`) - Contains scraping and data processing dependencies

**Package management:**
- Dependencies are managed via `pyproject.toml` files in each component
- UV provides fast dependency resolution and installation
- Virtual environments are created using `uv venv` and dependencies installed with `uv sync`

**Setup scripts:**
- `setup_backend.sh` - Automated setup for backend virtual environment using UV
- `setup_scripts.sh` - Automated setup for scripts virtual environment using UV

Virtual environments are excluded from version control via `.gitignore`.

## Folder Structure

The project is organized into three main components:

### `/scripts`
Contains data collection and processing scripts.

- **`/scripts/scrapers`** - Web scraping scripts for CubeCobra data
- **`/scripts/data_processing`** - Data transformation and cleaning scripts
- **`/scripts/.venv`** - Virtual environment for scripts (not committed to git)
- **`/scripts/pyproject.toml`** - Python dependencies and project metadata

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
- **`/backend/.venv`** - Virtual environment for backend (not committed to git)
- **`/backend/run.py`** - Development server script
- **`/backend/pyproject.toml`** - Python dependencies and project metadata

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