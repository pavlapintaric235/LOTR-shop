def test_catalog_routes_return_seeded_data(client) -> None:
    categories_response = client.get("/categories")
    assert categories_response.status_code == 200
    categories = categories_response.json()
    assert len(categories) == 3

    products_response = client.get("/products")
    assert products_response.status_code == 200
    products = products_response.json()
    assert len(products) == 10

    homepage_response = client.get("/homepage")
    assert homepage_response.status_code == 200
    homepage = homepage_response.json()
    assert len(homepage["featured_products"]) == 5
    assert len(homepage["most_wanted_products"]) == 8