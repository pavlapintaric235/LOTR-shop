def get_product_id_by_slug(client, slug: str) -> int:
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()

    for product in products:
        if product["slug"] == slug:
            return product["id"]

    raise AssertionError(f"Product with slug '{slug}' not found")


def create_paid_order_for_user(client, user_token) -> int:
    product_id = get_product_id_by_slug(client, "elven-cloak")

    add_response = client.post(
        "/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"product_id": product_id, "quantity": 1},
    )
    assert add_response.status_code == 200

    checkout_response = client.post(
        "/orders/checkout",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert checkout_response.status_code == 200
    order_id = checkout_response.json()["id"]

    pay_response = client.post(
        f"/payments/orders/{order_id}/pay",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"simulate_status": "success"},
    )
    assert pay_response.status_code == 200

    return order_id


def test_admin_can_list_orders(client, admin_token, user_token) -> None:
    order_id = create_paid_order_for_user(client, user_token)

    response = client.get(
        "/admin/orders",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    orders = response.json()
    assert any(order["id"] == order_id for order in orders)


def test_admin_can_get_single_order(client, admin_token, user_token) -> None:
    order_id = create_paid_order_for_user(client, user_token)

    response = client.get(
        f"/admin/orders/{order_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_admin_can_advance_order_status(client, admin_token, user_token) -> None:
    order_id = create_paid_order_for_user(client, user_token)

    processing_response = client.patch(
        f"/admin/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "processing"},
    )
    assert processing_response.status_code == 200
    assert processing_response.json()["status"] == "processing"

    shipped_response = client.patch(
        f"/admin/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "shipped"},
    )
    assert shipped_response.status_code == 200
    assert shipped_response.json()["status"] == "shipped"

    delivered_response = client.patch(
        f"/admin/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "delivered"},
    )
    assert delivered_response.status_code == 200
    assert delivered_response.json()["status"] == "delivered"


def test_admin_cannot_make_invalid_status_transition(client, admin_token, user_token) -> None:
    order_id = create_paid_order_for_user(client, user_token)

    response = client.patch(
        f"/admin/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "delivered"},
    )
    assert response.status_code == 400
    assert "Cannot transition order" in response.json()["detail"]


def test_non_admin_cannot_manage_orders(client, user_token) -> None:
    response = client.get(
        "/admin/orders",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"