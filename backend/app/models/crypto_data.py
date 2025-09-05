import uuid

from db.base import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, TIMESTAMP, DECIMAL, Float


class CryptocurrencyData(Base):
    __tablename__ = "cryptocurrency_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String, index=True, nullable=False)
    timestamp = Column(TIMESTAMP, unique=True, nullable=False)
    price_usd = Column(DECIMAL, nullable=False)
    daily_return = Column(Float, nullable=True)
