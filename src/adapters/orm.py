from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    inspect,
    event
)
from sqlalchemy.orm import clear_mappers, registry, relationship

from src.domain import model

metadata = MetaData()
mapper_registry = registry()

order_lines = Table(
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)

products = Table(
    "products",
    metadata,
    Column("sku", String(255), primary_key=True),
    Column("version_number", Integer, nullable=False, server_default="0"),
)

batches = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", ForeignKey("products.sku")),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


def start_mappers():
    orderline_mapper = inspect(model.OrderLine, raiseerr=False)
    batch_mapper = inspect(model.Batch, raiseerr=False)
    product_mapper = inspect(model.Product, raiseerr=False)

    # Tests and interactive runners can invoke mapper setup multiple times
    # in one process. Keep this function safe to call repeatedly.
    if (
        orderline_mapper is not None
        and batch_mapper is not None
        and product_mapper is not None
    ):
        return

    # If only one mapper exists, reset and rebuild a consistent mapping state.
    if (
        orderline_mapper is not None
        or batch_mapper is not None
        or product_mapper is not None
    ):
        clear_mappers()

    mapper_registry.map_imperatively(model.OrderLine, order_lines)

    batch_mapper = mapper_registry.map_imperatively(
        model.Batch,
        batches,
        properties={
            "_allocations": relationship(
                model.OrderLine,
                secondary=allocations,
                collection_class=set,
            )
        }
    )

    mapper_registry.map_imperatively(
        model.Product,
        products,
        properties={"batches": relationship(batch_mapper)},
    )

@event.listens_for(model.Product, "load")
def receive_load(product, _):
    product.events = []
