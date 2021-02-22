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
    endpoints: Dict[str, StatsItemSchema] = Field(default={})
    app: StatsItemSchema = Field(default_factory=StatsItemSchema)

    class Config:
        allow_mutation = False
