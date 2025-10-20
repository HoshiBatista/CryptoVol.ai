from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any


class SimulationJobBase(BaseModel):
    user_id: str
    portfolio_id: Optional[str] = None
    status: str  # pending, running, completed, failed


class SimulationJobCreate(SimulationJobBase):
    pass


class SimulationJobUpdate(BaseModel):
    status: Optional[str] = None


class SimulationJob(SimulationJobBase):
    id: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SimulationResultBase(BaseModel):
    job_id: str
    results: Dict[str, Any]
    model_id: str


class SimulationResultCreate(SimulationResultBase):
    pass


class SimulationResultUpdate(BaseModel):
    results: Optional[Dict[str, Any]] = None


class SimulationResult(SimulationResultBase):
    class Config:
        from_attributes = True


class SimulationJobWithResult(SimulationJob):
    result: Optional[SimulationResult] = None

    class Config:
        from_attributes = True
