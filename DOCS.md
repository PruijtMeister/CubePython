# Technical documentation

## Folder Structure

The project is organized into three main components:

### `/scripts`
Contains data collection and processing scripts.

- **`/scripts/scrapers`** - Web scraping scripts for CubeCobra data
- **`/scripts/data_processing`** - Data transformation and cleaning scripts

### `/backend`
FastAPI application serving the recommender engine.

- **`/backend/app`** - Main application code
  - **`/backend/app/models`** - SQLModel database models
  - **`/backend/app/api`** - API route handlers
  - **`/backend/app/core`** - Core configuration (database, settings)
  - **`/backend/app/services`** - Business logic and services
- **`/backend/tests`** - Backend test suite

### `/frontend`
React with TypeScript UI for inspecting data and recommendations.

- **`/frontend/src`** - Source code
  - **`/frontend/src/components`** - Reusable React components
  - **`/frontend/src/pages`** - Page components
  - **`/frontend/src/services`** - API client and service layer
  - **`/frontend/src/types`** - TypeScript type definitions
- **`/frontend/public`** - Static assets