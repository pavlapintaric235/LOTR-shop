def test_register_login_and_me_flow(client) -> None:
    register_response = client.post(
        "/auth/register",
        json={
            "email": "legolas@example.com",
            "username": "legolas",
            "password": "mirkwood123",
        },
    )
    assert register_response.status_code == 201
    assert register_response.json()["username"] == "legolas"

    login_response = client.post(
        "/auth/token",
        data={
            "username": "legolas",
            "password": "mirkwood123",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "legolas"