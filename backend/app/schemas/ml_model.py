from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any


class TrainedModelBase(BaseModel):
    crypto_id: int
    model_type: str  # GARCH, ARIMA
    parameters: Optional[Dict[str, Any]] = None
    version: int


class TrainedModelCreate(TrainedModelBase):
    pass


class TrainedModelUpdate(BaseModel):
    parameters: Optional[Dict[str, Any]] = None
    version: Optional[int] = None


class TrainedModel(TrainedModelBase):
    id: str
    trained_at: datetime

    class Config:
        from_attributes = True
