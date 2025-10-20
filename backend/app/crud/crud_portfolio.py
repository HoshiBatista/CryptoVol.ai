from typing import Optional, List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging_config import logger
from models.portfolio import Portfolio, PortfolioAsset
from schemas.portfolio import PortfolioCreate, PortfolioAssetCreate


async def get_portfolio_by_id(
    db: AsyncSession, portfolio_id: str
) -> Optional[Portfolio]:
    logger.info(f"Fetching portfolio by ID: {portfolio_id}")

    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    portfolio = result.scalars().first()

    if portfolio:
        logger.info(f"Portfolio found: {portfolio.id}")
    else:
        logger.info(f"Portfolio with ID {portfolio_id} not found")

    return portfolio


async def create_portfolio(
    db: AsyncSession, portfolio_in: PortfolioCreate
) -> Portfolio:
    logger.info(
        f"Creating portfolio for user ID: {portfolio_in.user_id} named '{portfolio_in.name}'"
    )

    db_portfolio = Portfolio(
        user_id=portfolio_in.user_id,
        name=portfolio_in.name,
    )
    db.add(db_portfolio)
    await db.commit()
    await db.refresh(db_portfolio)

    logger.info(f"Portfolio created successfully with ID: {db_portfolio.id}")

    return db_portfolio


async def get_portfolios_by_user(db: AsyncSession, user_id: str) -> List[Portfolio]:
    logger.info(f"Fetching portfolios for user ID: {user_id}")

    result = await db.execute(select(Portfolio).where(Portfolio.user_id == user_id))
    portfolios = result.scalars().all()

    logger.info(f"Fetched {len(portfolios)} portfolios for user ID: {user_id}")

    return portfolios


async def create_portfolio_asset(
    db: AsyncSession, asset_in: PortfolioAssetCreate
) -> PortfolioAsset:
    logger.info(
        f"Adding asset to portfolio ID: {asset_in.portfolio_id} (Crypto ID: {asset_in.crypto_id})"
    )

    db_asset = PortfolioAsset(
        portfolio_id=asset_in.portfolio_id,
        crypto_id=asset_in.crypto_id,
        amount=asset_in.amount,
    )
    db.add(db_asset)
    await db.commit()
    await db.refresh(db_asset)

    logger.info(f"Portfolio asset created successfully with ID: {db_asset.id}")

    return db_asset
