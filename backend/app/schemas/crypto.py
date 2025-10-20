from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class CryptocurrencyBase(BaseModel):
    symbol: str
    name: str
    description: Optional[str] = None


class CryptocurrencyCreate(CryptocurrencyBase):
    pass


class CryptocurrencyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Cryptocurrency(CryptocurrencyBase):
    id: int

    class Config:
        from_attributes = True


class CryptocurrencyDataBase(BaseModel):
    crypto_id: int
    timestamp: datetime
    price_usd: float
    daily_return: Optional[float] = None


class CryptocurrencyDataCreate(CryptocurrencyDataBase):
    pass


class CryptocurrencyDataUpdate(BaseModel):
    price_usd: Optional[float] = None
    daily_return: Optional[float] = None


class CryptocurrencyData(CryptocurrencyDataBase):
    id: str

    class Config:
        from_attributes = True
