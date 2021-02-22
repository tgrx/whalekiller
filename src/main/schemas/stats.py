from typing import Dict

from pydantic import BaseModel
from pydantic import Field


class StatsItemSchema(BaseModel):
    avg_seconds: float = Field(default=0.0)
    nr_requests: int = Field(default=0)
    seconds: float = Field(default=0.0)

    class Config:
        allow_mutation = False


class StatsSchema(BaseModel):
    app: StatsItemSchema = Field(default_factory=StatsItemSchema)
    endpoints: Dict[str, StatsItemSchema] = Field(default={})
    nr_vms: int = Field(default=0)

    class Config:
        allow_mutation = False
