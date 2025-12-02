import asyncio
import joblib
import numpy as np
from pathlib import Path
from uuid import UUID
from sqlalchemy import select

from app.crud import crud_dashboard
from app.core.logging_config import logger
from app.models.ml_model import TrainedModel
from app.models.simulation import SimulationResult
from app.models.crypto_data import CryptocurrencyData, Cryptocurrency


async def run_prediction_task(
    job_id: UUID, model_type: str, crypto_id: int, db_session_factory
):
    logger.info(f" Inference started for Job {job_id} [Model: {model_type}]")

    async with db_session_factory() as db:
        try:
            await crud_dashboard.update_simulation_status(db, job_id, "running")
            await asyncio.sleep(0.5)

            crypto_res = await db.execute(
                select(Cryptocurrency).where(Cryptocurrency.id == crypto_id)
            )
            crypto = crypto_res.scalars().first()
            if not crypto:
                raise ValueError(f"Cryptocurrency with ID {crypto_id} not found.")

            stmt = select(TrainedModel).where(
                TrainedModel.crypto_id == crypto_id,
                TrainedModel.model_type == model_type,
            )
            db_model = (await db.execute(stmt)).scalars().first()

            if not db_model:
                raise ValueError(
                    f"No trained '{model_type}' model found for {crypto.symbol} in DB. "
                    "Please upload models and run 'scripts/register_models.py'."
                )

            model_path_str = db_model.parameters.get("path")
            if not model_path_str:
                raise ValueError("Model path is missing in database record.")

            model_path = Path(model_path_str)
            if not model_path.exists():
                raise FileNotFoundError(f"Model file missing on disk: {model_path}")

            logger.info(f"📂 Loading model from: {model_path}")
            loaded_model = joblib.load(model_path)

            horizon_days = 30
            result_payload = {}

            dates = [f"+{i}d" for i in range(1, horizon_days + 1)]

            if model_type == "GARCH":
                forecast = loaded_model.forecast(horizon=horizon_days, reindex=False)

                variance_values = forecast.variance.values[-1, :]

                vol_forecast_pct = np.sqrt(variance_values)

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
                    "prices": [last_price] * horizon_days,  # Плоская линия цены
                    "volatility": vol_forecast_pct.tolist(),  # График волатильности
                    "confidence_interval": None,  # GARCH не дает интервалов цены
                    "metrics": {
                        "Avg_Volatility_30d": f"{np.mean(vol_forecast_pct):.2f}%",
                        "Current_Price": f"${last_price:,.2f}",
                    },
                }

            elif model_type == "ARIMA":
                forecast_res = loaded_model.get_forecast(steps=horizon_days)

                pred_prices = forecast_res.predicted_mean
                conf_int = forecast_res.conf_int(alpha=0.05)

                result_payload = {
                    "type": "ARIMA",
                    "dates": dates,
                    "prices": pred_prices.tolist(),  # График цены
                    "volatility": [0] * horizon_days,  # Пустой график волатильности
                    "confidence_interval": {
                        "upper": conf_int.iloc[:, 1].tolist(),
                        "lower": conf_int.iloc[:, 0].tolist(),
                    },
                    "metrics": {
                        "Target_Price_30d": f"${pred_prices.iloc[-1]:,.2f}",
                        "Trend": "Bullish 🟢"
                        if pred_prices.iloc[-1] > pred_prices.iloc[0]
                        else "Bearish 🔴",
                    },
                }

            else:
                raise ValueError(f"Unknown model type: {model_type}")

            logger.info(" Saving simulation results...")
            db_result = SimulationResult(
                job_id=job_id, results=result_payload, model_id=db_model.id
            )
            db.add(db_result)

            await crud_dashboard.update_simulation_status(db, job_id, "completed")
            logger.info("✅ Inference completed successfully.")

        except Exception as e:
            logger.exception(f"❌ Inference failed: {e}")
            await crud_dashboard.update_simulation_status(db, job_id, "failed")
