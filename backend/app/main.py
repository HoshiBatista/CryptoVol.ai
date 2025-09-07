import uvicorn
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import logger
from app.db.session import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    yield
    logger.info("Application shutdown...")


app = FastAPI(
    title="CryptoVol.ai API [Minimal]",
    description="Базовый запуск для проверки БД и создания миграций.",
    version="0.0.1",
    lifespan=lifespan,
)


@app.get("/", tags=["Health Check"])
async def root():
    logger.info("Root endpoint was hit.")
    return {"status": "ok", "message": "API is running."}


@app.get("/db-check", tags=["Health Check"])
async def check_db_connection(db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Проверяет соединение с базой данных, выполняя простой запрос.
    Критически важен для проверки, что приложение "видит" БД в Docker.
    """
    try:
        await db.execute(text("SELECT 1"))
        logger.info("Database connection check successful.")
        return {"status": "ok", "message": "Database connection is healthy."}
    except Exception as e:
        logger.critical(f"Database connection check FAILED: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not connect to the database: {e}",
        )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
