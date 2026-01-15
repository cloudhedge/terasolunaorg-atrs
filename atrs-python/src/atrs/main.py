"""ATRS FastAPI Application Entry Point"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .config.database import get_database_manager
from .api import api_router
from .core.exceptions import AtrsBusinessException, FlightNotFoundException, InvalidFlightException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - connect/disconnect database"""
    # Startup
    db_manager = get_database_manager()
    await db_manager.connect()
    print(f"Connected to database: {settings.database_url.split('@')[-1]}")

    yield

    # Shutdown
    await db_manager.disconnect()
    print("Disconnected from database")


app = FastAPI(
    title="ATRS - Airline Ticket Reservation System",
    description="Python/FastAPI migration of ATRS Java application",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(AtrsBusinessException)
async def atrs_business_exception_handler(request: Request, exc: AtrsBusinessException):
    """Handle business logic exceptions"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": exc.error_code.value,
            "message": str(exc),
            "details": exc.details,
        },
    )


@app.exception_handler(FlightNotFoundException)
async def flight_not_found_exception_handler(request: Request, exc: FlightNotFoundException):
    """Handle flight not found exceptions"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": str(exc)},
    )


@app.exception_handler(InvalidFlightException)
async def invalid_flight_exception_handler(request: Request, exc: InvalidFlightException):
    """Handle invalid flight exceptions"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": str(exc)},
    )


# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "app": settings.app_name}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": "ATRS - Airline Ticket Reservation System",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "atrs.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
