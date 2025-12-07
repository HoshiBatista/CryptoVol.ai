import asyncio
import joblib
import numpy as np
from pathlib import Path
from uuid import UUID
from sqlalchemy import select

from app.crud import crud_dashboard
from app.core.logging_config import logger
from app.models.crypto_data import CryptocurrencyData
from app.models.ml_model import TrainedModel
from app.models.simulation import SimulationResult

MODELS_DIR = Path("/app/ml_models")


async def run_prediction_task(
    job_id: UUID, model_type: str, crypto_id: int, db_session_factory
):
    """
    Фоновая задача для запуска инференса.
    """
    logger.info(
        f"🚀 Inference started for Job {job_id} [Model: {model_type}, CryptoID: {crypto_id}]"
    )

    async with db_session_factory() as db:
        try:
            await crud_dashboard.update_simulation_status(db, job_id, "running")
            await asyncio.sleep(0.5)

            stmt = select(TrainedModel).where(
                TrainedModel.crypto_id == crypto_id,
                TrainedModel.model_type == model_type,
            )

            db_model = (await db.execute(stmt)).scalars().first()

            if not db_model:
                raise ValueError(
                    f"No trained model found for CryptoID={crypto_id} Type={model_type}. Please run model training/import."
                )

            stored_path = db_model.parameters.get("path")
            if not stored_path:
                raise ValueError("Model path not found in DB parameters")

            model_path = Path(stored_path)
            if not model_path.is_absolute():
                model_path = Path("/app") / model_path

            if not model_path.exists():
                filename = model_path.name
                model_path = MODELS_DIR / filename
                if not model_path.exists():
                    raise FileNotFoundError(f"Model file missing: {model_path}")

            logger.info(f"📂 Loading model from {model_path}...")
            loaded_model = joblib.load(model_path)

            horizon = 30
            dates = [f"+{i}d" for i in range(1, horizon + 1)]
            result_payload = {}

            if model_type == "GARCH":
                forecast = loaded_model.forecast(horizon=horizon, reindex=False)
                vol_forecast_pct = np.sqrt(forecast.variance.values[-1, :])

                price_stmt = (
                    select(CryptocurrencyData.price_usd)
                    .where(CryptocurrencyData.crypto_id == crypto_id)
                    .order_by(CryptocurrencyData.timestamp.desc())
                    .limit(1)
                )
                last_price = float(
                    (await db.execute(price_stmt)).scalars().first() or 0
                )

                result_payload = {
                    "type": "GARCH",
                    "dates": dates,
                    "prices": [last_price] * horizon,
                    "volatility": vol_forecast_pct.tolist(),
                    "confidence_interval": None,
                    "metrics": {
                        "Avg_Volatility": round(float(np.mean(vol_forecast_pct)), 2),
                        "Current_Price": round(last_price, 2),
                    },
                }

            elif model_type == "ARIMA":
                forecast_res = loaded_model.get_forecast(steps=horizon)
                pred_prices = forecast_res.predicted_mean
                conf_int = forecast_res.conf_int(alpha=0.05)

                result_payload = {
                    "type": "ARIMA",
                    "dates": dates,
                    "prices": pred_prices.tolist(),
                    "volatility": [0] * horizon,
                    "confidence_interval": {
                        "upper": conf_int.iloc[:, 1].tolist(),
                        "lower": conf_int.iloc[:, 0].tolist(),
                    },
                    "metrics": {
                        "Target_Price": round(float(pred_prices.iloc[-1]), 2),
                        "Trend": "Bullish"
                        if pred_prices.iloc[-1] > pred_prices.iloc[0]
                        else "Bearish",
                    },
                }

            db_result = SimulationResult(
                job_id=job_id, results=result_payload, model_id=db_model.id
            )
            db.add(db_result)

            await crud_dashboard.update_simulation_status(db, job_id, "completed")
            logger.info(f"✅ Job {job_id} completed successfully.")

        except Exception as e:
            logger.exception(f"❌ Job {job_id} failed: {e}")
            await crud_dashboard.update_simulation_status(db, job_id, "failed")
