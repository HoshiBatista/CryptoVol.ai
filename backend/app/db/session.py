from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.config import config

engine = create_async_engine(config.postgres_url, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    Зависимость FastAPI, которая создает и предоставляет асинхронную сессию БД для одного запроса.
    Гарантирует, что сессия всегда будет закрыта после выполнения запроса.
    """
    async with AsyncSessionLocal() as session:
        yield session
