import requests

from src import config
from src.entrypoints.fastapi_app import AddBatchDescriptor
from test.random_refs import random_batchref, random_orderid, random_sku


def post_to_add_batch(ref, sku, qty, eta):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/add_batch", json=AddBatchDescriptor(ref=ref, sku=sku, qty=qty, eta=eta).model_dump()
    )
    return r

def post_to_allocate(orderid, sku, qty):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/allocate", json={"orderid": orderid, "sku": sku, "qty": qty}
    )
    return r

def get_allocations(orderid):
    url = config.get_api_url()
    r = requests.get(f"{url}/allocations/{orderid}")
    return r

def test_happy_path_returns_201_and_allocated_batch():
    orderid = random_orderid()
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    post_to_add_batch(laterbatch, sku, 100, "2011-01-02")
    post_to_add_batch(earlybatch, sku, 100, "2011-01-01")
    post_to_add_batch(otherbatch, othersku, 100, None)

    r = post_to_allocate(orderid, sku, qty=3)
    assert r.status_code == 202
    assert r.json()["msg"] == "Ok"

    r = get_allocations(orderid)
    assert r.status_code == 200
    assert r.json() == [
        {"sku": sku, "batchref": earlybatch},
    ]

def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, orderid = random_sku(), random_orderid()

    r = post_to_allocate(orderid, unknown_sku, qty=20)
    assert r.status_code == 400
    assert r.json()["detail"] == f"Invalid sku {unknown_sku}"

    r = get_allocations(orderid)
    assert r.status_code == 404

