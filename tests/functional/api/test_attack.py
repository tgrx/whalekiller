from functools import partial
from typing import Collection
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


def find_vm(
    config: CloudConfigSchema,
    *,
    name: Optional[str] = None,
    tag: Optional[str] = None,
    tags: Optional[Collection[str]] = None,
    vm_id: Optional[str] = None,
) -> VirtualMachineSchema:
    for vm in config.vms:
        this = all(
            (
                name is None or vm.name == name,
                vm_id is None or vm.vm_id == vm_id,
                tag is None or tag in vm.tags,
                tags is None or set(tags).issubset(vm.tags),
            )
        )
        if this:
            return vm
    raise ValueError("no vm found")


@pytest.mark.functional
@pytest.mark.asyncio
async def test_positive_0(service_url, config_0):
    config_0: CloudConfigSchema

    bastion = find_vm(config_0, name="bastion")
    jira_server = find_vm(config_0, name="jira_server")

    attack_vectors = [
        (bastion, [bastion]),
        (jira_server, [bastion]),
    ]

    await validate_attack_vectors(service_url, attack_vectors)


@pytest.mark.functional
@pytest.mark.asyncio
async def test_positive_1(service_url, config_1):
    config_1: CloudConfigSchema
    find_vm_ = partial(find_vm, config_1)

    billing_service = find_vm_(name="billing service")
    etcd_node = find_vm_(name="etcd node", tags=[])
    etcd_node_dev_api = find_vm_(name="etcd node", tags=["dev", "api"])
    frontend_server = find_vm_(name="frontend server")
    jira_server = find_vm_(name="jira server")
    k8s_node_http_ci = find_vm_(name="k8s node", tags=["http", "ci"])
    k8s_node_windows_dc = find_vm_(name="k8s node", tags=["windows-dc"])
    kafka_8d2 = find_vm_(name="kafka", vm_id="vm-8d2d12765")
    kafka_f27 = find_vm_(name="kafka", vm_id="vm-f270036588")
    rabbitmq = find_vm_(name="rabbitmq")

    attack_vectors = [
        (billing_service, []),
        (etcd_node, []),
        (etcd_node_dev_api, []),
        (frontend_server, []),
        (jira_server, []),
        (k8s_node_http_ci, []),
        (k8s_node_windows_dc, []),
        (kafka_8d2, []),
        (kafka_f27, []),
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
