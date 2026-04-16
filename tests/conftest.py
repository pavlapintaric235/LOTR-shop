from collections.abc import Generator
import asyncio

import pytest
from fastapi.testclient import TestClient

from app.db.base_class import Base
from app.db.session import get_db_session
from app.db.testing import get_test_db_session, test_engine
from app.main import app

# Force model imports so Base.metadata contains all tables
from app.models.cart import Cart  # noqa: F401
from app.models.cart_item import CartItem  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.order import Order  # noqa: F401
from app.models.order_item import OrderItem  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.user import User  # noqa: F401


async def reset_test_database() -> None:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    asyncio.run(reset_test_database())

    app.dependency_overrides[get_db_session] = get_test_db_session

    with TestClient(app) as test_client:
        reset_response = test_client.post("/testing/reset")
        assert reset_response.status_code == 204
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client: TestClient) -> str:
    response = client.post(
        "/auth/token",
        data={
            "username": "frodo",
            "password": "shire123",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def user_token(client: TestClient) -> str:
    response = client.post(
        "/auth/token",
        data={
            "username": "sam",
            "password": "shire123",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]