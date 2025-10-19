from app.db.base import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", back_populates="portfolios")
    assets = relationship(
        "PortfolioAsset", back_populates="portfolio", cascade="all, delete-orphan"
    )
    simulation_jobs = relationship(
        "SimulationJob", back_populates="portfolio", cascade="all, delete-orphan"
    )


class PortfolioAsset(Base):
    __tablename__ = "portfolio_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    portfolio_id = Column(
        UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False
    )
    crypto_id = Column(Integer, ForeignKey("cryptocurrencies.id"), nullable=False)
    amount = Column(DECIMAL(24, 12), nullable=False)

    portfolio = relationship("Portfolio", back_populates="assets")
    crypto = relationship("Cryptocurrency", back_populates="portfolio_assets")
