import asyncio
import random
from uuid import UUID
from app.crud import crud_dashboard
from app.core.logging_config import logger


async def run_prediction_task(job_id: UUID, model_type: str, db_session_factory):
    logger.info(f"🚀 Starting ML job {job_id} using {model_type}")

    async with db_session_factory() as db:
        try:
            await crud_dashboard.update_simulation_status(db, job_id, "running")

            await asyncio.sleep(5)

            fake_dates = [f"Day {i}" for i in range(1, 8)]
            fake_volatility = [random.uniform(0.02, 0.08) for _ in range(7)]
            fake_price_path = [random.uniform(40000, 45000) for _ in range(7)]

            prediction_result = {  # F841 # noqa: F841
                "dates": fake_dates,
                "volatility_forecast": fake_volatility,
                "price_simulation": fake_price_path,
                "confidence_interval": 0.95,
            }

            # TODO: Здесь нужно получить реальный ID модели из таблицы trained_models
            # Пока захардкодим UUID или создадим фиктивный, если нет в БД
            # Но для примера пропустим создание SimulationResult с FK constraint issue
            # В реальном коде нужно сначала найти model_id

            logger.info(f"✅ Job {job_id} completed successfully")

            # Внимание: тут нужен реальный model_id из БД.
            # Для теста просто обновим статус на completed,
            # но в crud нужно передать results и model_id
            await crud_dashboard.update_simulation_status(db, job_id, "completed")

        except Exception as e:
            logger.error(f"❌ Job {job_id} failed: {e}")
            await crud_dashboard.update_simulation_status(db, job_id, "failed")
