from uuid import UUID
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import logger
from app.models.crypto_data import Cryptocurrency
from app.models.portfolio import Portfolio, PortfolioAsset
from app.models.simulation import SimulationJob, SimulationResult
from app.schemas.dashboard import PortfolioCreate, SimulationCreate


async def create_portfolio(
    db: AsyncSession, user_id: UUID, portfolio_in: PortfolioCreate
) -> Portfolio:
    logger.info(f"Creating portfolio '{portfolio_in.name}' for user {user_id}")

    db_portfolio = Portfolio(user_id=user_id, name=portfolio_in.name)
    db.add(db_portfolio)
    await db.flush()

    for asset in portfolio_in.assets:
        db_asset = PortfolioAsset(
            portfolio_id=db_portfolio.id, crypto_id=asset.crypto_id, amount=asset.amount
        )
        db.add(db_asset)

    await db.commit()
    await db.refresh(db_portfolio)
    return db_portfolio


async def get_user_portfolios(db: AsyncSession, user_id: UUID) -> List[Portfolio]:
    query = (
        select(Portfolio)
        .where(Portfolio.user_id == user_id)
        .options(selectinload(Portfolio.assets).selectinload(PortfolioAsset.crypto))
    )

    result = await db.execute(query)
    return result.scalars().all()


async def get_portfolio_by_id(
    db: AsyncSession, portfolio_id: UUID, user_id: UUID
) -> Optional[Portfolio]:
    query = (
        select(Portfolio)
        .where(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
        .options(selectinload(Portfolio.assets).selectinload(PortfolioAsset.crypto))
    )

    result = await db.execute(query)
    return result.scalars().first()


async def create_simulation_job(
    db: AsyncSession, user_id: UUID, sim_in: SimulationCreate
) -> SimulationJob:
    db_job = SimulationJob(
        user_id=user_id, portfolio_id=sim_in.portfolio_id, status="pending"
    )
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    return db_job


async def get_user_simulations(db: AsyncSession, user_id: UUID) -> List[SimulationJob]:
    query = (
        select(SimulationJob)
        .where(SimulationJob.user_id == user_id)
        .order_by(desc(SimulationJob.created_at))
        .options(selectinload(SimulationJob.result))
    )

    result = await db.execute(query)
    return result.scalars().all()


async def update_simulation_status(
    db: AsyncSession,
    job_id: UUID,
    status: str,
    results: Optional[dict] = None,
    model_id: Optional[UUID] = None,
):
    query = select(SimulationJob).where(SimulationJob.id == job_id)
    result_exec = await db.execute(query)
    job = result_exec.scalars().first()

    if job:
        job.status = status
        if status == "completed":
            from datetime import datetime

            job.completed_at = datetime.now()

            if results and model_id:
                db_result = SimulationResult(
                    job_id=job_id, results=results, model_id=model_id
                )
                db.add(db_result)

        await db.commit()


async def get_all_cryptos(db: AsyncSession) -> List[Cryptocurrency]:
    result = await db.execute(select(Cryptocurrency).order_by(Cryptocurrency.id))
    return result.scalars().all()
