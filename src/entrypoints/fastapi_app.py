import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src import config
from src.adapters import orm, repository
from src.domain import model
from src.service_layer import services, unit_of_work

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

@app.post("/allocate", status_code=status.HTTP_201_CREATED, response_model=AllocateResponse)
def allocate_endpoint(data: AllocateDescriptor):
    try:
        batchref = services.allocate(
            data.orderid,
            data.sku,
            data.qty,
            unit_of_work.SqlAlchemyUnitOfWork(),
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return AllocateResponse(batchref=batchref)

@app.post("/add_batch", status_code=status.HTTP_201_CREATED, response_model=AddBatchResponse)
def add_batch(data: AddBatchDescriptor):
    try:
        services.add_batch(
            data.ref,
            data.sku,
            data.qty,
            datetime.datetime.fromisoformat(data.eta).date() if data.eta else None,
            unit_of_work.SqlAlchemyUnitOfWork(),
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return AddBatchResponse(msg="Ok")


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
