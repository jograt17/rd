import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from main import app
from app.dependency import get_engine, get_product_repository, get_product_service
from app.service.product_service import ProductService

import os

os.environ["TESTING"] = "true"


@pytest.fixture()
def mock_repo():
    repo = MagicMock()
    repo.create_product.return_value = 123
    return repo


@pytest.fixture()
def mock_engine():
    return MagicMock()


@pytest.fixture()
def client(mock_engine, mock_repo):
    app.dependency_overrides[get_engine] = lambda: mock_engine
    app.dependency_overrides[get_product_repository] = lambda: mock_repo
    app.dependency_overrides[get_product_service] = lambda: ProductService(mock_engine, mock_repo)

    yield TestClient(app)

    app.dependency_overrides.clear()
