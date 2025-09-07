from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db
from app.core.logging_config import logger

router = APIRouter()


@router.get(
    "/health-check", status_code=status.HTTP_200_OK, summary="Check API and DB status"
)
async def health_check(db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Проверяет работоспособность API и доступность соединения с базой данных.

    - **Возвращает 200 OK**, если API работает и база данных доступна.
    - **Возвращает 503 Service Unavailable**, если не удается подключиться к базе данных.
    """
    api_status = {"status": "ok", "service": "API"}
    db_status = {}

    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar_one() == 1:
            logger.info("Database connection health check successful.")
            db_status = {"status": "ok", "service": "Database"}
        else:
            raise Exception("Database returned an unexpected result.")

    except Exception as e:
        logger.critical(f"Database connection health check failed: {e}", exc_info=False)
        db_status = {"status": "error", "service": "Database", "details": str(e)}

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"api": api_status, "database": db_status},
        )

    return {"api": api_status, "database": db_status}
