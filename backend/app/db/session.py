from typing import AsyncGenerator
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import config
from app.core.logging_config import logger
from app.models.crypto_data import Cryptocurrency

engine = create_async_engine(config.postgres_url, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

async_session_factory = AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость FastAPI, которая создает и предоставляет асинхронную сессию БД для одного запроса.
    Гарантирует, что сессия всегда будет закрыта после выполнения запроса.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db_data():
    async with async_session_factory() as db:
        try:
            logger.info("🔧 Enabling UUID extension in Database...")
            await db.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            await db.commit()
        except Exception as e:
            logger.warning(
                f"Could not enable uuid-ossp extension (might be already enabled or permissions issue): {e}"
            )
            await db.rollback()

        result = await db.execute(select(Cryptocurrency))
        existing = result.scalars().first()

        if not existing:
            logger.info("🌱 Seeding database with initial Cryptocurrencies...")
            coins = [
                Cryptocurrency(
                    id=1, symbol="BTC", name="Bitcoin", description="Digital Gold"
                ),
                Cryptocurrency(
                    id=2, symbol="ETH", name="Ethereum", description="Smart Contracts"
                ),
                Cryptocurrency(
                    id=3, symbol="SOL", name="Solana", description="High Speed L1"
                ),
                Cryptocurrency(
                    id=4, symbol="TON", name="Toncoin", description="The Open Network"
                ),
                Cryptocurrency(
                    id=5,
                    symbol="BNB",
                    name="Binance Coin",
                    description="Exchange Token",
                ),
            ]
            db.add_all(coins)
            await db.commit()
            logger.info("✅ Database seeded successfully!")
