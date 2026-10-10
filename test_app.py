import pytest
from app import app, orders


@pytest.fixture
def client():
    app.config["TESTING"] = True
    orders.clear()
    with app.test_client() as client:
        yield client


def valid_order():
    return {"customer": "Afridi", "item": "Laptop", "quantity": 1}


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200


def test_create_order_success(client):
    res = client.post("/orders", json=valid_order())
    assert res.status_code == 202
    assert res.get_json()["status"] == "RECEIVED"


def test_create_order_missing_field(client):
    res = client.post("/orders", json={"customer": "Afridi"})
    assert res.status_code == 400


def test_create_order_bad_quantity(client):
    data = valid_order()
    data["quantity"] = -5
    assert client.post("/orders", json=data).status_code == 400


def test_get_order(client):
    oid = client.post("/orders", json=valid_order()).get_json()["order_id"]
    res = client.get(f"/orders/{oid}")
    assert res.status_code == 200
    assert res.get_json()["item"] == "Laptop"


def test_get_unknown_order(client):
    assert client.get("/orders/nope").status_code == 404
