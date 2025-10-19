from app.db.base import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, String, DateTime, ForeignKey


class SimulationJob(Base):
    __tablename__ = "simulation_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"))
    status = Column(
        String, nullable=False, default="pending"
    )  # pending, running, completed, failed
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="simulation_jobs")
    portfolio = relationship("Portfolio", back_populates="simulation_jobs")
    result = relationship(
        "SimulationResult",
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )


class SimulationResult(Base):
    __tablename__ = "simulation_results"

    job_id = Column(
        UUID(as_uuid=True), ForeignKey("simulation_jobs.id"), primary_key=True
    )
    results = Column(JSONB, nullable=False)  # Распределение цен, VaR и т.д.
    model_id = Column(
        UUID(as_uuid=True), ForeignKey("trained_models.id"), nullable=False
    )

    job = relationship("SimulationJob", back_populates="result")
    model = relationship("TrainedModel")
