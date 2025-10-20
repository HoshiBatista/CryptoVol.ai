from sqlalchemy.future import select
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging_config import logger
from models.ml_model import TrainedModel
from schemas.ml_model import TrainedModelCreate


async def get_trained_model_by_id(
    db: AsyncSession, model_id: str
) -> Optional[TrainedModel]:
    logger.info(f"Fetching trained model by ID: {model_id}")

    result = await db.execute(select(TrainedModel).where(TrainedModel.id == model_id))
    model = result.scalars().first()

    if model:
        logger.info(f"Trained model found: {model.id}, type: {model.model_type}")
    else:
        logger.info(f"Trained model with ID {model_id} not found")

    return model


async def get_latest_trained_model_by_crypto_and_type(
    db: AsyncSession, crypto_id: int, model_type: str
) -> Optional[TrainedModel]:
    logger.info(f"Fetching latest {model_type} model for crypto ID: {crypto_id}")

    result = await db.execute(
        select(TrainedModel)
        .where(
            TrainedModel.crypto_id == crypto_id, TrainedModel.model_type == model_type
        )
        .order_by(TrainedModel.version.desc())
        .limit(1)
    )
    model = result.scalars().first()

    if model:
        logger.info(
            f"Latest {model_type} model found for crypto ID {crypto_id}: {model.id}, version {model.version}"
        )
    else:
        logger.info(f"No {model_type} model found for crypto ID {crypto_id}")

    return model


async def create_trained_model(
    db: AsyncSession, model_in: TrainedModelCreate
) -> TrainedModel:
    logger.info(
        f"Creating new {model_in.model_type} model for crypto ID: {model_in.crypto_id}"
    )

    db_model = TrainedModel(
        crypto_id=model_in.crypto_id,
        model_type=model_in.model_type,
        parameters=model_in.parameters,
        version=model_in.version,
    )
    db.add(db_model)
    await db.commit()
    await db.refresh(db_model)

    logger.info(
        f"Trained model created successfully with ID: {db_model.id}, version {db_model.version}"
    )

    return db_model
