def get_product_id_by_slug(client, slug: str) -> int:
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()

    for product in products:
        if product["slug"] == slug:
            return product["id"]

    raise AssertionError(f"Product with slug '{slug}' not found")


def test_cannot_checkout_empty_cart(client, user_token) -> None:
    response = client.post(
        "/orders/checkout",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Cart is empty"


def test_checkout_cart_creates_order_and_clears_cart(client, user_token) -> None:
    product_id = get_product_id_by_slug(client, "elven-cloak")

    add_response = client.post(
        "/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "product_id": product_id,
            "quantity": 2,
        },
    )
    assert add_response.status_code == 200

    checkout_response = client.post(
        "/orders/checkout",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert checkout_response.status_code == 200

    order = checkout_response.json()
    assert order["status"] == "pending"
    assert len(order["items"]) == 1
    assert order["items"][0]["quantity"] == 2

    cart_response = client.get(
        "/cart",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert cart_response.status_code == 200
    assert cart_response.json()["items"] == []


def test_list_orders_returns_user_orders(client, user_token) -> None:
    product_id = get_product_id_by_slug(client, "sting-replica")

    add_response = client.post(
        "/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "product_id": product_id,
            "quantity": 1,
        },
    )
    assert add_response.status_code == 200

    checkout_response = client.post(
        "/orders/checkout",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert checkout_response.status_code == 200
    order_id = checkout_response.json()["id"]

    orders_response = client.get(
        "/orders",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert orders_response.status_code == 200
    orders = orders_response.json()
    assert len(orders) >= 1
    assert any(order["id"] == order_id for order in orders)


def test_get_single_order_returns_order(client, user_token) -> None:
    product_id = get_product_id_by_slug(client, "red-book-of-westmarch")

    add_response = client.post(
        "/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "product_id": product_id,
            "quantity": 1,
        },
    )
    assert add_response.status_code == 200

    checkout_response = client.post(
        "/orders/checkout",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert checkout_response.status_code == 200
    order_id = checkout_response.json()["id"]

    order_response = client.get(
        f"/orders/{order_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert order_response.status_code == 200
    assert order_response.json()["id"] == order_id