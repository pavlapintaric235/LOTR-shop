from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db_session
from app.db.testing import get_test_db_session
from app.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
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