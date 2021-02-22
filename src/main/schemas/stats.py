from typing import Dict

from pydantic import BaseModel
from pydantic import Field


class StatsItemSchema(BaseModel):
    avg_seconds: float = Field(default=0.0)
    nr_requests: int = Field(default=0)
    seconds: float = Field(default=0.0)

    class Config:
        allow_mutation = False


class DynamicAppStatsSchema(BaseModel):
    endpoints: Dict[str, StatsItemSchema] = Field(default={})

    @property
    def app(self):
        avg_seconds = 0.0
        nr_requests = 0
        seconds = 0.0

        for endpoint in self.endpoints.values():
            avg_seconds += endpoint.seconds
            nr_requests += endpoint.nr_requests
            seconds += endpoint.seconds

        avg_seconds /= nr_requests or 1

        stats = StatsItemSchema(
            avg_seconds=avg_seconds,
            nr_requests=nr_requests,
            seconds=seconds,
        )

        return stats


class AppStatsSchema(BaseModel):
    endpoints: Dict[str, StatsItemSchema] = Field(default={})
    app: StatsItemSchema

    class Config:
        allow_mutation = False
