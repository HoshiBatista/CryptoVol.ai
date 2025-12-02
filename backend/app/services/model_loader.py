import json
from pathlib import Path
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.logging_config import logger
from app.models.ml_model import TrainedModel
from app.db.session import async_session_factory
from app.models.crypto_data import Cryptocurrency

MODELS_DIR = Path("/app/ml_models")
METADATA_FILE = MODELS_DIR / "models_metadata.json"


async def reload_models_in_db():
    if not METADATA_FILE.exists():
        logger.warning(
            f"⚠️ No models metadata found at {METADATA_FILE}. Skipping model loading."
        )
        return

    logger.info(f"🔄 Auto-loading models from {METADATA_FILE}...")

    try:
        with open(METADATA_FILE, "r") as f:
            metadata_list = json.load(f)

        async with async_session_factory() as db:
            crypto_map = {}
            all_cryptos = (await db.execute(select(Cryptocurrency))).scalars().all()
            for c in all_cryptos:
                crypto_map[c.symbol] = c.id

            count = 0
            for item in metadata_list:
                symbol = item["symbol"]
                if symbol not in crypto_map:
                    continue

                crypto_id = crypto_map[symbol]
                model_type = item["model_type"]

                file_path = str(MODELS_DIR / item["filename"])

                full_params = {**item["parameters"], "path": file_path}

                stmt = select(TrainedModel).where(
                    TrainedModel.crypto_id == crypto_id,
                    TrainedModel.model_type == model_type,
                )
                existing = (await db.execute(stmt)).scalars().first()

                now_utc = datetime.now(timezone.utc)

                if existing:
                    existing.parameters = full_params
                    existing.trained_at = now_utc
                    existing.version += 1
                else:
                    new_model = TrainedModel(
                        crypto_id=crypto_id,
                        model_type=model_type,
                        parameters=full_params,
                        version=1,
                        trained_at=now_utc,
                    )
                    db.add(new_model)
                count += 1

            await db.commit()
            logger.info(f"✅ Successfully loaded {count} models into DB.")

    except Exception as e:
        logger.error(f"❌ Failed to auto-load models: {e}")
