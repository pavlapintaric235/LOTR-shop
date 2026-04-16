def test_admin_routes_require_auth(client) -> None:
    category_response = client.post(
        "/admin/categories",
        json={
            "slug": "admin-test-category",
            "name": "Admin Test Category",
        },
    )
    assert category_response.status_code == 401


def test_admin_can_create_category(client, admin_token) -> None:
    response = client.post(
        "/admin/categories",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "slug": "collectibles",
            "name": "Collectibles",
        },
    )
    assert response.status_code == 201
    assert response.json()["slug"] == "collectibles"


def test_non_admin_cannot_create_category(client, user_token) -> None:
    response = client.post(
        "/admin/categories",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "slug": "collectibles",
            "name": "Collectibles",
        },
    )
    assert response.status_code == 403