from pydantic import BaseModel
from pydantic import Field


class FirewallRuleSchema(BaseModel):
    fw_id: str = Field(...)
    source_tag: str = Field(...)
    dest_tag: str = Field(...)
