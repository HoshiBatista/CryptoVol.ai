from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class PortfolioBase(BaseModel):
    name: str
    user_id: str


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(BaseModel):
    name: Optional[str] = None


class Portfolio(PortfolioBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class PortfolioAssetBase(BaseModel):
    portfolio_id: str
    crypto_id: int
    amount: float


class PortfolioAssetCreate(PortfolioAssetBase):
    pass


class PortfolioAssetUpdate(BaseModel):
    amount: Optional[float] = None


class PortfolioAsset(PortfolioAssetBase):
    id: str

    class Config:
        from_attributes = True


class PortfolioWithAssets(Portfolio):
    assets: List["PortfolioAsset"] = []

    class Config:
        from_attributes = True
