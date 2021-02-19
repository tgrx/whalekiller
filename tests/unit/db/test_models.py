import pytest
from sqlalchemy import select

from main.db import FirewallRule
from main.db import Tag
from main.db import VirtualMachine


@pytest.mark.unit
@pytest.mark.asyncio
async def test_models(session):
    async with session.begin():
        tag_a, tag_b = tags = [Tag(name=i) for i in "ab"]
        session.add_all(tags)

        vm = VirtualMachine(
            tags=tags,
            vm_id="vm-xxx-1",
        )
        session.add(vm)

        fw = FirewallRule(
            dest=tag_b,
            fw_id="fw-xxx-1",
            source=tag_a,
        )
        session.add(fw)

    async with session.begin():
        stmt = select(VirtualMachine)
        results = await session.execute(stmt)
        vms = list(results.scalars())

    assert len(vms) == 1

    vm = vms[0]
    assert vm.vm_id == "vm-xxx-1"
    assert vm.name is None
    assert len(vm.tags) == 2
    assert {t.name for t in vm.tags} == {"a", "b"}
