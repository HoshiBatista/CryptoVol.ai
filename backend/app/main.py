import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging_config import logger
from app.api.endpoints import auth, users, health


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

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(health.router, prefix="/api", tags=["Health Check"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
