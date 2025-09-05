import uuid

from app.db.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, String, DECIMAL, ForeignKey


class PortfolioAndSimulations(Base):
    __tablename__ = "portfolio_and_simulations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False)
    amount = Column(DECIMAL, nullable=False)
    projected_value = Column(JSONB)

    owner = relationship("User", back_populates="portfolios")
