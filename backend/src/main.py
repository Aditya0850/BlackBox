from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
import redis.asyncio as redis
from minio import Minio
from minio.error import S3Error
import logging
from alembic import command
from alembic.config import Config
import os

from .config import get_settings, Settings

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title=get_settings().PROJECT_NAME,
        version=get_settings().VERSION,
        openapi_url=f"{get_settings().API_V1_STR}/openapi.json",
    )

    # CORS middleware - adjust origins as needed
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For development, restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Startup event to ensure MinIO bucket exists and run migrations
    @app.on_event("startup")
    async def startup_event():
        settings = get_settings()
        # Ensure MinIO bucket exists
        try:
            minio_client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
            bucket_name = settings.MINIO_BUCKET
            if not minio_client.bucket_exists(bucket_name):
                minio_client.make_bucket(bucket_name)
                logger.info(f"Created MinIO bucket: {bucket_name}")
            else:
                logger.info(f"MinIO bucket already exists: {bucket_name}")
        except Exception as e:
            logger.error(f"Failed to ensure MinIO bucket exists on startup: {e}")
            # We don't fail the startup because the health check will report the issue

        # Run database migrations
        try:
            # Construct the database URL for Alembic (using psycopg2, not asyncpg)
            db_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
            # Alembic configuration
            alembic_cfg = Config()
            # Set the script location to the alembic directory relative to this file
            # We need to get the absolute path to the alembic directory inside the container
            # Assuming the alembic directory is copied to /app/alembic
            alembic_cfg.set_main_option("script_location", "/app/alembic")
            alembic_cfg.set_main_option("sqlalchemy.url", db_url)
            # Run the migration
            command.upgrade(alembic_cfg, "head")
            logger.info("Database migrations applied successfully")
        except Exception as e:
            logger.error(f"Failed to apply database migrations on startup: {e}")
            # We don't fail the startup because the health check will report the issue

    # Health check endpoint
    @app.get("/health")
    async def health_check(settings: Settings = Depends(get_settings)):
        checks = {}
        overall_status = "ok"

        # Check PostgreSQL
        try:
            # We'll create an async engine on the fly for the check
            from sqlalchemy.ext.asyncio import create_async_engine
            engine = create_async_engine(
                f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}",
                echo=False,
            )
            async with engine.connect() as conn:
                # Check that we can run a query
                await conn.execute(text("SELECT 1"))
                # Check that schemas exist
                result = await conn.execute(
                    text("SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('intel', 'audit')")
                )
                schemas = [row[0] for row in result]
                if "intel" not in schemas or "audit" not in schemas:
                    raise Exception("Missing required schemas")
            await engine.dispose()
            checks["postgres"] = "ok"
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            checks["postgres"] = f"failed: {str(e)}"
            overall_status = "failed"

        # Check Redis
        try:
            r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
            await r.ping()
            await r.close()
            checks["redis"] = "ok"
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            checks["redis"] = f"failed: {str(e)}"
            overall_status = "failed"

        # Check MinIO
        try:
            minio_client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
            # Check if bucket exists
            if not minio_client.bucket_exists(settings.MINIO_BUCKET):
                raise Exception(f"Bucket {settings.MINIO_BUCKET} does not exist")
            checks["minio"] = "ok"
        except S3Error as e:
            logger.error(f"MinIO health check failed: {e}")
            checks["minio"] = f"failed: {str(e)}"
            overall_status = "failed"
        except Exception as e:
            logger.error(f"MinIO health check failed: {e}")
            checks["minio"] = f"failed: {str(e)}"
            overall_status = "failed"

        if overall_status == "ok":
            return {"status": "ok", "checks": checks}
        else:
            # Return 503 if any check failed
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"status": "failed", "checks": checks},
            )

    # Include API routers (we'll create the v1 router later)
    from .api.v1 import api_router
    app.include_router(api_router, prefix=get_settings().API_V1_STR)

    return app

app = create_app()