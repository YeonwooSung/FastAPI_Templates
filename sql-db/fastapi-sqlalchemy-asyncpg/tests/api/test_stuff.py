from uuid import UUID

import pytest
from fastapi import status
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize(
    "payload, status_code",
    (
        (
            {"name": "motorhead", "description": "we play rock and roll"},
            status.HTTP_201_CREATED,
        ),
    ),
)
async def test_add_stuff(client: AsyncClient, payload: dict, status_code: int):
    response = await client.post("/stuff", json=payload)
    assert response.status_code == status_code
    assert payload["name"] == response.json()["name"]


@pytest.mark.parametrize(
    "payload, status_code",
    (
        (
            {"name": "motorhead-0", "description": "we play rock and roll"},
            status.HTTP_200_OK,
        ),
    ),
)
async def test_get_stuff(client: AsyncClient, payload: dict, status_code: int):
    await client.post("/stuff", json=payload)
    name = payload["name"]
    response = await client.get(f"/stuff/{name}")
    assert response.status_code == status_code
    assert payload["name"] == response.json()["name"]
    assert UUID(response.json()["id"])


@pytest.mark.parametrize(
    "payload, status_code",
    (
        (
            {"name": "motorhead-1", "description": "we play rock and roll"},
            status.HTTP_200_OK,
        ),
    ),
)
async def test_delete_stuff(client: AsyncClient, payload: dict, status_code: int):
    response = await client.post("/stuff", json=payload)
    print(response.json())
    name = response.json()["name"]
    response = await client.delete(f"/stuff/{name}")
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "payload, status_code",
    (
        (
            {"name": "motorhead", "description": "we play rock and roll"},
            status.HTTP_200_OK,
        ),
    ),
)
@pytest.mark.parametrize(
    "patch_payload, patch_status_code",
    (
        (
            {"name": "motorhead", "description": "we play loud"},
            status.HTTP_200_OK,
        ),
    ),
)
async def test_update_stuff(
    client: AsyncClient,
    payload: dict,
    status_code: int,
    patch_payload: dict,
    patch_status_code: int,
):
    await client.post("/stuff", json=payload)
    name = payload["name"]
    response = await client.patch(f"/stuff/{name}", json=patch_payload)
    assert response.status_code == patch_status_code
    response = await client.get(f"/stuff/{name}")
    assert patch_payload["description"] == response.json()["description"]
