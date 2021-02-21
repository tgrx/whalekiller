from typing import List

from pydantic import BaseModel
from pydantic import Field

from main.schemas.firewall_rule import FirewallRuleSchema
from main.schemas.virtual_machine import VirtualMachineSchema


class CloudConfigSchema(BaseModel):
    vms: List[VirtualMachineSchema] = Field(default_factory=[])
    fw_rules: List[FirewallRuleSchema] = Field(default_factory=[])
