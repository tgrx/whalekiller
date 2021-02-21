from typing import List

from pydantic import BaseModel
from pydantic import Field


class VirtualMachineSchema(BaseModel):
    vm_id: str = Field(...)
    name: str = Field(default="")
    tags: List[str] = Field(default_factory=list)
