from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import settings, init_db
from app.api.health import router as health_router
from app.api.cards import router as cards_router
from app.services.card_database import CardDatabase


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()

    # Initialize CardDatabase
    print("Initializing CardDatabase...")
    app.state.card_db = await CardDatabase.create()
    print("CardDatabase initialized successfully")

    yield
    # Shutdown
    # Add cleanup logic here if needed


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    lifespan=lifespan,
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix=settings.api_v1_prefix, tags=["health"])
app.include_router(cards_router, prefix=f"{settings.api_v1_prefix}/cards", tags=["cards"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to CubePython API",
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }
