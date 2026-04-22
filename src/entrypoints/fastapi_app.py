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
from src.service_layer import services

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
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    line = model.OrderLine(
        data.orderid, data.sku, data.qty,
    )

    try:
        batchref = services.allocate(data.orderid, data.sku, data.qty, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return AllocateResponse(batchref=batchref)

@app.post("/add_batch", status_code=status.HTTP_201_CREATED, response_model=AddBatchResponse)
def add_batch(data: AddBatchDescriptor):
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    eta = data.eta
    if eta is not None:
        eta = datetime.datetime.fromisoformat(eta).date()
    services.add_batch(
        data.ref,
        data.sku,
        data.qty,
        eta,
        repo,
        session,
    )
    return AddBatchResponse(msg="Ok")


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
