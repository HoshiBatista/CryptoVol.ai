from app.db.base import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey


class TrainedModel(Base):
    __tablename__ = "trained_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    crypto_id = Column(Integer, ForeignKey("cryptocurrencies.id"), nullable=False)
    model_type = Column(String, nullable=False)  # GARCH, ARIMA
    parameters = Column(JSONB)
    trained_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    version = Column(Integer, nullable=False)

    crypto = relationship("Cryptocurrency", back_populates="models")
    simulation_results = relationship("SimulationResult", back_populates="model")
