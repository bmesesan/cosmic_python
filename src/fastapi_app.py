import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src import config, model, orm, repository, services

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = FastAPI()

class AllocateDescriptor(BaseModel):
    orderid: str
    sku: str
    qty: int

class AllocateResponse(BaseModel):
    batchref: str


@app.post("/allocate", status_code=status.HTTP_201_CREATED, response_model=AllocateResponse)
def allocate_endpoint(data: AllocateDescriptor):
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    line = model.OrderLine(
        data.orderid, data.sku, data.qty,
    )

    try:
        batchref = services.allocate(line, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return AllocateResponse(batchref=batchref)

uvicorn.run(app, host="0.0.0.0", port=8000)
