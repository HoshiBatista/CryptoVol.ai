from sqlalchemy.sql import func
from typing import Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging_config import logger
from models.simulation import SimulationJob, SimulationResult
from schemas.simulation import SimulationJobCreate, SimulationResultCreate


async def get_simulation_job_by_id(
    db: AsyncSession, job_id: str
) -> Optional[SimulationJob]:
    logger.info(f"Fetching simulation job by ID: {job_id}")

    result = await db.execute(select(SimulationJob).where(SimulationJob.id == job_id))
    job = result.scalars().first()

    if job:
        logger.info(f"Simulation job found: {job.id}, status: {job.status}")
    else:
        logger.info(f"Simulation job with ID {job_id} not found")

    return job


async def create_simulation_job(
    db: AsyncSession, job_in: SimulationJobCreate
) -> SimulationJob:
    logger.info(
        f"Creating simulation job for user ID: {job_in.user_id}, status: {job_in.status}"
    )

    db_job = SimulationJob(
        user_id=job_in.user_id,
        portfolio_id=job_in.portfolio_id,
        status=job_in.status,
    )
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)

    logger.info(f"Simulation job created successfully with ID: {db_job.id}")

    return db_job


async def update_simulation_job_status(
    db: AsyncSession, job_id: str, new_status: str
) -> Optional[SimulationJob]:
    logger.info(f"Updating simulation job ID {job_id} status to '{new_status}'")

    result = await db.execute(select(SimulationJob).where(SimulationJob.id == job_id))
    db_job = result.scalars().first()

    if not db_job:
        logger.warning(f"Attempt to update non-existent simulation job ID: {job_id}")
        return None

    old_status = db_job.status
    db_job.status = new_status

    if new_status == "completed":
        db_job.completed_at = func.now()

    await db.commit()
    await db.refresh(db_job)

    logger.info(
        f"Simulation job ID {job_id} status updated from '{old_status}' to '{new_status}'"
    )

    return db_job


async def create_simulation_result(
    db: AsyncSession, result_in: SimulationResultCreate
) -> SimulationResult:
    logger.info(f"Creating simulation result for job ID: {result_in.job_id}")

    db_result = SimulationResult(
        job_id=result_in.job_id,
        results=result_in.results,
        model_id=result_in.model_id,
    )
    db.add(db_result)
    await db.commit()
    await db.refresh(db_result)

    logger.info(
        f"Simulation result created successfully for job ID: {result_in.job_id}"
    )

    return db_result
