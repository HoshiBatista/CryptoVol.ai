from app.db.base import Base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    DECIMAL,
    Float,
    ForeignKey,
    Text,
)


class Cryptocurrency(Base):
    __tablename__ = "cryptocurrencies"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(16), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    data_points = relationship(
        "CryptocurrencyData", back_populates="crypto", cascade="all, delete-orphan"
    )
    models = relationship(
        "TrainedModel", back_populates="crypto", cascade="all, delete-orphan"
    )
    portfolio_assets = relationship(
        "PortfolioAsset", back_populates="crypto", cascade="all, delete-orphan"
    )


class CryptocurrencyData(Base):
    __tablename__ = "cryptocurrency_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    crypto_id = Column(Integer, ForeignKey("cryptocurrencies.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    price_usd = Column(DECIMAL(18, 8), nullable=False)
    daily_return = Column(Float)

    crypto = relationship("Cryptocurrency", back_populates="data_points")

    __table_args__ = ({"sqlite_autoincrement": True},)
