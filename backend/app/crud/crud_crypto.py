from typing import Optional, List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging_config import logger
from models.crypto_data import Cryptocurrency, CryptocurrencyData
from schemas.crypto import CryptocurrencyCreate, CryptocurrencyDataCreate


async def get_cryptocurrency_by_symbol(
    db: AsyncSession, symbol: str
) -> Optional[Cryptocurrency]:
    logger.info(f"Fetching cryptocurrency by symbol: {symbol}")

    result = await db.execute(
        select(Cryptocurrency).where(Cryptocurrency.symbol == symbol)
    )
    crypto = result.scalars().first()

    if crypto:
        logger.info(f"Cryptocurrency found: {crypto.id}")
    else:
        logger.info(f"Cryptocurrency with symbol {symbol} not found")

    return crypto


async def create_cryptocurrency(
    db: AsyncSession, crypto_in: CryptocurrencyCreate
) -> Cryptocurrency:
    logger.info(f"Creating cryptocurrency with symbol: {crypto_in.symbol}")

    db_crypto = Cryptocurrency(
        symbol=crypto_in.symbol,
        name=crypto_in.name,
        description=crypto_in.description,
    )

    db.add(db_crypto)
    await db.commit()
    await db.refresh(db_crypto)

    logger.info(f"Cryptocurrency created successfully with ID: {db_crypto.id}")

    return db_crypto


async def get_cryptocurrency_data_by_crypto_id(
    db: AsyncSession, crypto_id: int
) -> List[CryptocurrencyData]:
    logger.info(f"Fetching data points for cryptocurrency ID: {crypto_id}")

    result = await db.execute(
        select(CryptocurrencyData)
        .where(CryptocurrencyData.crypto_id == crypto_id)
        .order_by(CryptocurrencyData.timestamp.desc())
    )

    data_points = result.scalars().all()

    logger.info(
        f"Fetched {len(data_points)} data points for cryptocurrency ID: {crypto_id}"
    )

    return data_points


async def create_cryptocurrency_data(
    db: AsyncSession, data_in: CryptocurrencyDataCreate
) -> CryptocurrencyData:
    logger.info(
        f"Creating data point for cryptocurrency ID: {data_in.crypto_id} at {data_in.timestamp}"
    )

    db_data = CryptocurrencyData(
        crypto_id=data_in.crypto_id,
        timestamp=data_in.timestamp,
        price_usd=data_in.price_usd,
        daily_return=data_in.daily_return,
    )

    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)

    logger.info(f"Data point created successfully with ID: {db_data.id}")

    return db_data
