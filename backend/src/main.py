from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
import redis.asyncio as redis
from minio import Minio
from minio.error import S3Error
import logging

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

        # Check Minio
        try:
            minio_client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
            # Check if bucket exists
            if not minio_client.bucket_exists(settings.MINIO_BUCKET):
                # Try to create it (if permissions allow)
                minio_client.make_bucket(settings.MINIO_BUCKET)
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