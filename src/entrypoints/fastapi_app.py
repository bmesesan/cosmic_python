import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src import config
from src.adapters import orm
from src.domain import commands
from src.service_layer import handlers, messagebus, unit_of_work

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = FastAPI()

class AllocateDescriptor(BaseModel):
    orderid: str
    sku: str
    qty: int

class AllocateResponse(BaseModel):
    batchref: str

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
        messagebus.handle(cmd, unit_of_work.SqlAlchemyUnitOfWork())
    except (handlers.InvalidSku) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return AddBatchResponse(msg="Ok")

@app.post("/allocate", status_code=status.HTTP_201_CREATED, response_model=AllocateResponse)
def allocate_endpoint(data: AllocateDescriptor):
    try:
        cmd = commands.Allocate(
            data.orderid, data.sku, data.qty
        )

        results = messagebus.handle(cmd, unit_of_work.SqlAlchemyUnitOfWork())
        batchref = results.pop(0)

    except (handlers.InvalidSku) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return AllocateResponse(batchref=batchref)


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
