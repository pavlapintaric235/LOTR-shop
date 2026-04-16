def test_health_route_returns_200(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_unknown_route_returns_404(client) -> None:
    response = client.get("/no-such-route")
    assert response.status_code == 404


def test_user_me_requires_auth(client) -> None:
    response = client.get("/users/me")
    assert response.status_code == 401


def test_admin_route_requires_admin(client, user_token) -> None:
    response = client.get(
        "/admin/orders",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"