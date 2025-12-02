from pydantic import BaseModel, UUID4
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class PortfolioAssetBase(BaseModel):
    crypto_id: int
    amount: Decimal


class PortfolioAssetCreate(PortfolioAssetBase):
    pass


class PortfolioAssetOut(PortfolioAssetBase):
    id: UUID4
    symbol: str

    class Config:
        from_attributes = True


class PortfolioCreate(BaseModel):
    name: str
    assets: List[PortfolioAssetCreate] = []


class PortfolioOut(BaseModel):
    id: UUID4
    name: str
    created_at: datetime
    assets: List[PortfolioAssetOut] = []

    class Config:
        from_attributes = True


class SimulationCreate(BaseModel):
    portfolio_id: Optional[UUID4] = None
    crypto_id: Optional[int] = None
    model_type: str = "GARCH"
    parameters: Dict[str, Any] = {}


class SimulationResultOut(BaseModel):
    results: Dict[str, Any]
    model_type: str


class SimulationJobOut(BaseModel):
    id: UUID4
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[SimulationResultOut] = None

    class Config:
        from_attributes = True


class CryptoOut(BaseModel):
    id: int
    symbol: str
    name: str

    class Config:
        from_attributes = True
