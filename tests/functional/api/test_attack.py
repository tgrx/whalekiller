from itertools import dropwhile
from typing import NoReturn
from typing import Optional
from typing import Sequence
from typing import Tuple

import pytest
from httpx import AsyncClient
from starlette import status

from main.asgi import app
from main.schemas import CloudConfigSchema
from main.schemas import VirtualMachineSchema

AttackVectorT = Tuple[VirtualMachineSchema, Sequence[VirtualMachineSchema]]
AttackVectorsT = Sequence[AttackVectorT]


@pytest.mark.functional
@pytest.mark.asyncio
async def test_positive_0(service_url, config_0):
    config_0: CloudConfigSchema

    bastion = next(dropwhile(lambda vm: vm.name != "bastion", config_0.vms))
    jira_server = next(dropwhile(lambda vm: vm.name != "jira_server", config_0.vms))

    attack_vectors = [
        (bastion, [bastion]),
        (jira_server, [bastion]),
    ]

    await validate_attack_vectors(service_url, attack_vectors)


@pytest.mark.functional
@pytest.mark.asyncio
async def test_positive_1(service_url, config_1):
    config_1: CloudConfigSchema

    etcd_node = next(dropwhile(lambda vm: vm.name != "etcd node", config_1.vms))
    jira_server = next(dropwhile(lambda vm: vm.name != "jira server", config_1.vms))
    # k8s_node_http_ci = next(dropwhile(lambda vm: vm.name != "jira_server" or not {"http", "ci"}.issubset(vm.tags), config_1.vms))
    # k8s_node_windows_dc = next(dropwhile(lambda vm: vm.name != "jira_server" or not {"windows-dc"}.issubset(vm.tags), config_1.vms))
    kafka = next(dropwhile(lambda vm: vm.name != "kafka", config_1.vms))
    rabbitmq = next(dropwhile(lambda vm: vm.name != "rabbitmq", config_1.vms))

    attack_vectors = [
        (etcd_node, []),
        (jira_server, []),
        # (k8s_node_http_ci, []),
        # (k8s_node_windows_dc, []),
        (kafka, []),
        (rabbitmq, []),
    ]

    await validate_attack_vectors(service_url, attack_vectors)


@pytest.mark.functional
@pytest.mark.asyncio
async def test_negative(service_url):
    async with AsyncClient(app=app, base_url=service_url) as client:
        response = await client.get("/api/v1/attack")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def validate_attack_vectors(
    service_url: str, attack_vectors: AttackVectorsT
) -> Optional[NoReturn]:
    async with AsyncClient(app=app, base_url=service_url) as client:
        for honeypot, attackers in attack_vectors:
            response = await client.get(f"/api/v1/attack?vm_id={honeypot.vm_id}")
            assert (
                response.status_code == status.HTTP_200_OK
            ), f"failed {response} on {honeypot}"

            payload = response.json()
            attackers_actual = set(payload)

            attackers_expected = {attacker.vm_id for attacker in attackers}

            assert attackers_expected == attackers_actual, f"failed for {honeypot}"
