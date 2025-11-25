from typing import Annotated, List
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db, async_session_factory

from app.schemas.dashboard import (
    PortfolioCreate,
    PortfolioOut,
    SimulationCreate,
    SimulationJobOut,
)
from app.crud import crud_dashboard
from app.services.inference import run_prediction_task
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


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
