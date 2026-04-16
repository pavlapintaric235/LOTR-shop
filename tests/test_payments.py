def get_product_id_by_slug(client, slug: str) -> int:
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()

    for product in products:
        if product["slug"] == slug:
            return product["id"]

    raise AssertionError(f"Product with slug '{slug}' not found")


def create_order_for_user(client, user_token) -> int:
    product_id = get_product_id_by_slug(client, "elven-cloak")

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

    return checkout_response.json()["id"]


def test_fake_payment_success_marks_order_paid(client, user_token) -> None:
    order_id = create_order_for_user(client, user_token)

    response = client.post(
        f"/payments/orders/{order_id}/pay",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"simulate_status": "success"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["payment_status"] == "paid"
    assert body["payment_provider"] == "fakepay"
    assert body["order_status"] == "confirmed"
    assert body["payment_reference"] is not None


def test_fake_payment_failed_marks_order_failed(client, user_token) -> None:
    order_id = create_order_for_user(client, user_token)

    response = client.post(
        f"/payments/orders/{order_id}/pay",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"simulate_status": "failed"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["payment_status"] == "failed"
    assert body["payment_provider"] == "fakepay"
    assert body["order_status"] == "payment_failed"
    assert body["payment_reference"] is not None


def test_cannot_pay_order_twice(client, user_token) -> None:
    order_id = create_order_for_user(client, user_token)

    first_response = client.post(
        f"/payments/orders/{order_id}/pay",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"simulate_status": "success"},
    )
    assert first_response.status_code == 200

    second_response = client.post(
        f"/payments/orders/{order_id}/pay",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"simulate_status": "success"},
    )
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Order is already paid"


def test_get_order_payment_status(client, user_token) -> None:
    order_id = create_order_for_user(client, user_token)

    pay_response = client.post(
        f"/payments/orders/{order_id}/pay",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"simulate_status": "success"},
    )
    assert pay_response.status_code == 200

    status_response = client.get(
        f"/payments/orders/{order_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert status_response.status_code == 200
    body = status_response.json()
    assert body["order_id"] == order_id
    assert body["payment_status"] == "paid"
    assert body["order_status"] == "confirmed"