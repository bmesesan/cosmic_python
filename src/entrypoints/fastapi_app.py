import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from src.domain import commands
from src.service_layer import handlers
from src import bootstrap, views

bus = bootstrap.bootstrap()
app = FastAPI()

class AllocateDescriptor(BaseModel):
    orderid: str
    sku: str
    qty: int

class AllocateResponse(BaseModel):
    msg: str

class AddBatchDescriptor(BaseModel):
    ref: str
    sku: str
    qty: int
    eta: Optional[str]

class AddBatchResponse(BaseModel):
    msg: str

@app.post("/add_batch", status_code=status.HTTP_201_CREATED, response_model=AddBatchResponse)
def add_batch(data: AddBatchDescriptor):
    eta = data.eta
    if eta is not None:
        eta = datetime.datetime.fromisoformat(eta).date()

    try:
        cmd = commands.CreateBatch(
            data.ref, data.sku, data.qty, eta
        )
        bus.handle(cmd)
    except (handlers.InvalidSku) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return AddBatchResponse(msg="Ok")

@app.post("/allocate", status_code=status.HTTP_202_ACCEPTED, response_model=AllocateResponse)
def allocate_endpoint(data: AllocateDescriptor):
    try:
        cmd = commands.Allocate(
            data.orderid, data.sku, data.qty
        )

        bus.handle(cmd)

    except (handlers.InvalidSku) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return AllocateResponse(msg="Ok")

@app.get("/allocations/{orderid}", status_code=status.HTTP_200_OK)
def allocations_view_endpoint(orderid: str):
    allocations = views.allocations(orderid, bus.uow)

    if not allocations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")

    return allocations

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
