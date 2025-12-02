from typing import Annotated, List
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db, async_session_factory

from app.schemas.dashboard import (
    PortfolioCreate,
    PortfolioOut,
    SimulationCreate,
    SimulationJobOut,
)
from app.models.user import User
from app.crud import crud_dashboard
from app.api.deps import get_current_user
from app.services.market_data import sync_market_data
from app.services.inference import run_prediction_task
from app.services.model_loader import reload_models_in_db
from app.models.crypto_data import Cryptocurrency
from app.models.ml_model import TrainedModel

router = APIRouter()


@router.post("/sync-data")
async def sync_crypto_data(
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Запускает фоновую задачу: скачивание данных с Yahoo Finance.
    Не блокирует UI.
    """

    async def _bg_sync_task():
        async with async_session_factory() as db:
            await sync_market_data(db)

    background_tasks.add_task(_bg_sync_task)

    return {
        "status": "Sync started",
        "message": "Market data update is running in background",
    }


@router.get("/portfolios", response_model=List[PortfolioOut])
async def read_portfolios(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await crud_dashboard.get_user_portfolios(db, user_id=current_user.id)


@router.post("/portfolios", response_model=PortfolioOut)
async def create_portfolio(
    portfolio_in: PortfolioCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await crud_dashboard.create_portfolio(
        db, user_id=current_user.id, portfolio_in=portfolio_in
    )


@router.post("/predict", response_model=SimulationJobOut)
async def run_simulation(
    sim_in: SimulationCreate,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # 1. Создаем запись Job в БД
    job = await crud_dashboard.create_simulation_job(
        db, user_id=current_user.id, sim_in=sim_in
    )

    # 2. Отправляем задачу в фон
    # Теперь async_session_factory передается корректно
    background_tasks.add_task(
        run_prediction_task, job.id, sim_in.model_type, async_session_factory
    )

    return job


@router.get("/simulations", response_model=List[SimulationJobOut])
async def get_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await crud_dashboard.get_user_simulations(db, user_id=current_user.id)


@router.get("/cryptos")
async def get_cryptos(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Cryptocurrency).order_by(Cryptocurrency.symbol))
    return result.scalars().all()


@router.get("/active-models")
async def get_active_models(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = (
        select(TrainedModel)
        .options(selectinload(TrainedModel.crypto))
        .order_by(TrainedModel.model_type)
    )
    result = await db.execute(stmt)
    models = result.scalars().all()

    data = []
    for m in models:
        data.append(
            {
                "id": str(m.id),
                "symbol": m.crypto.symbol,
                "type": m.model_type,
                "version": m.version,
                "trained_at": m.trained_at,
                "parameters": m.parameters,
            }
        )
    return data


@router.post("/reload-models")
async def reload_models_api(current_user: Annotated[User, Depends(get_current_user)]):
    await reload_models_in_db()
    return {"status": "ok", "message": "Models reloaded from disk"}
