# tests/test_product.py
def test_create_product(client, mock_repo):
    mock_repo.get_product_by_sku.return_value = None
    payload = {"name": "RK Keyboard", "sku": "KB-001", "price": 22.22, "stock_quantity": 1}

    response = client.post("/api/products", json=payload)
    print(response.content)

    assert response.status_code == 201
    assert "product" in response.json()["data"]
    mock_repo.create_product.assert_called_once()


def test_create_duplicate_sku_product(client, mock_repo):
    mock_repo.get_product_by_sku.return_value = True
    payload = {"name": "RK Keyboard", "sku": "KB-001", "price": 22.22, "stock_quantity": 1}

    response = client.post("/api/products", json=payload)
    print(response.content)

    assert response.status_code == 422
    assert response.json()["message"] == "SKU Exists"
