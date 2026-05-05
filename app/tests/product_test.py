# import pytest
from fastapi.testclient import TestClient
from app.main import app

# from app.model.product_model import ProductCreateModel
# from app.service.product_service import ProductService

client = TestClient(app=app)


# @pytest.fixture
# def product_create_mock_request():
#     return {"name": "Bottle", "sku": "BTL-001", "price": 500.00, "stock_quantity": 5}


def create_product_happy_path():
    # mock_repo = mocker.Mock()
    # mock_repo.create_product.result_value = 1

    # service = ProductService(mock_repo)

    # response = client.post("/products", json=product_create_mock_request())
    # assert(result)
    # assert response.status_code == 200
    response = client.get("/")
    assert response.status_code == 200
