def get_product_id_by_slug(client, slug: str) -> int:
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()

    for product in products:
        if product["slug"] == slug:
            return product["id"]

    raise AssertionError(f"Product with slug '{slug}' not found")


def test_get_empty_cart(client, user_token) -> None:
    response = client.get(
        "/cart",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_add_item_to_cart(client, user_token) -> None:
    product_id = get_product_id_by_slug(client, "elven-cloak")

    response = client.post(
        "/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "product_id": product_id,
            "quantity": 2,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 2
    assert body["items"][0]["product"]["id"] == product_id


def test_add_same_item_twice_increments_quantity(client, user_token) -> None:
    product_id = get_product_id_by_slug(client, "elven-cloak")

    first_response = client.post(
        "/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "product_id": product_id,
            "quantity": 1,
        },
    )
    assert first_response.status_code == 200

    second_response = client.post(
        "/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "product_id": product_id,
            "quantity": 2,
        },
    )
    assert second_response.status_code == 200
    body = second_response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 3


def test_update_cart_item_quantity(client, user_token) -> None:
    product_id = get_product_id_by_slug(client, "sting-replica")

    create_response = client.post(
        "/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "product_id": product_id,
            "quantity": 1,
        },
    )
    assert create_response.status_code == 200
    item_id = create_response.json()["items"][0]["id"]

    update_response = client.put(
        f"/cart/items/{item_id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "quantity": 2,
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["items"][0]["quantity"] == 2


def test_delete_cart_item(client, user_token) -> None:
    product_id = get_product_id_by_slug(client, "red-book-of-westmarch")

    create_response = client.post(
        "/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "product_id": product_id,
            "quantity": 1,
        },
    )
    assert create_response.status_code == 200
    item_id = create_response.json()["items"][0]["id"]

    delete_response = client.delete(
        f"/cart/items/{item_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["items"] == []


def test_cannot_add_more_than_stock(client, user_token) -> None:
    product_id = get_product_id_by_slug(client, "sting-replica")

    response = client.post(
        "/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "product_id": product_id,
            "quantity": 999,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Requested quantity exceeds available stock"