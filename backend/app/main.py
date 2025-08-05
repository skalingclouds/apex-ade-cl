from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.api.api import api_router
from app.core.database import engine
from app.models import Base
from app.core.error_handlers import (
    ExtractionError, extraction_error_handler,
    database_error_handler, general_error_handler
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    # Close database connections, cleanup, etc.

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

# Register exception handlers
app.add_exception_handler(ExtractionError, extraction_error_handler)
app.add_exception_handler(SQLAlchemyError, database_error_handler)
app.add_exception_handler(Exception, general_error_handler)

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}