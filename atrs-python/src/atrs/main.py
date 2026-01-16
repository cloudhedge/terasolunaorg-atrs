"""FastAPI application entry point.

ATRS - Airline Ticket Reservation System
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api import api_router
from .config.database import database
from .core.exceptions import AtrsException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.
    
    Handles database connection on startup and shutdown.
    """
    # Startup
    await database.connect()
    yield
    # Shutdown
    await database.disconnect()


app = FastAPI(
    title="ATRS API",
    description="Airline Ticket Reservation System - Python/FastAPI",
    version="1.0.0",
    lifespan=lifespan,
)


# Exception handler for business exceptions
@app.exception_handler(AtrsException)
async def atrs_exception_handler(request: Request, exc: AtrsException):
    """Handle ATRS business exceptions.
    
    Returns JSON response with error code and message.
    """
    return JSONResponse(
        status_code=400,
        content={
            "code": exc.code,
            "message": exc.message,
        },
    )


# Include API router
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {"status": "ok", "app": "ATRS", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
