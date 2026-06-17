from contextlib import asynccontextmanager
from typing import Annotated

import psycopg2
import psycopg2.extras
from psycopg2 import pool
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

import uuid

from services.product_orders import (
    CreateOrderInput,
    GetOrderInput,
    GetOrdersInput,
    UpdateOrderInput,
    create_order_service,
    get_order_service,
    get_orders_service,
    update_order_service,
)
from services.products import (
    GetProductStockInput,
    UpdateProductInput,
    UpdateProductStockInput,
    get_product_stock_service,
    update_product_service,
    update_product_stock_service,
)

psycopg2.extras.register_uuid()

db_pool: pool.ThreadedConnectionPool | None = None


class CreateProductOrderRequest(BaseModel):
    product_id: uuid.UUID
    count: int


class CommonHeaders(BaseModel):
    x_user_id: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool

    print("Server is starting up...")

    db_pool = pool.ThreadedConnectionPool(
        2,
        10,
        host="localhost",
        dbname="inventory-order-sys",
        user="postgres",
        password="postgres",
        port=5432,
    )

    yield  # The app serves requests while paused here
    # --- Shutdown Callback Logic ---
    print("Application is shutting down...")
    print("Disconnecting from DB...")
    db_pool.closeall()
    # Your cleanup callbacks go here (e.g., closing sessions, freeing memory)


app = FastAPI(lifespan=lifespan)


@app.get("/product/{product_id}/stock")
async def get_product_stock(product_id: uuid.UUID):
    assert db_pool is not None
    db_connection = db_pool.getconn()

    try:
        data = get_product_stock_service(
            GetProductStockInput(connection=db_connection, product_id=product_id)
        )
        return {"data": data}

    except psycopg2.Error:
        db_connection.rollback()
        raise HTTPException(status_code=400, detail="Unable to get product stock")

    finally:
        db_pool.putconn(db_connection)


@app.get("/orders")
async def get_orders(
    headers: Annotated[CommonHeaders, Header()], limit: int = 10, offset: int = 0
):
    assert db_pool is not None

    header_dict = dict(headers)
    user_id = header_dict["x_user_id"]
    db_connection = db_pool.getconn()

    try:
        data = get_orders_service(
            GetOrdersInput(
                connection=db_connection, user_id=user_id, limit=limit, offset=offset
            )
        )
        return {"data": data}

    except psycopg2.Error:
        db_connection.rollback()
        raise HTTPException(status_code=400, detail="Unable to get product order")
    finally:
        db_pool.putconn(db_connection)


@app.post("/orders")
async def create_order(
    headers: Annotated[CommonHeaders, Header()], request: CreateProductOrderRequest
):
    assert db_pool is not None

    product_order_dict = request.model_dump()
    header_dict = dict(headers)

    db_connection = db_pool.getconn()

    user_id = header_dict["x_user_id"]
    product_id = product_order_dict["product_id"]
    product_count = product_order_dict["count"]
    try:
        update_product_stock_res = update_product_stock_service(
            UpdateProductStockInput(
                connection=db_connection, stock=product_count, product_id=product_id
            )
        )

        if not update_product_stock_res.success:
            db_connection.rollback()
            raise HTTPException(
                status_code=400, detail="Product not found or out of stock"
            )

        product_order_item = create_order_service(
            CreateOrderInput(
                connection=db_connection,
                product_id=product_id,
                user_id=user_id,
                product_count=product_count,
            )
        )

        db_connection.commit()
        return {"data": product_order_item}

    except psycopg2.Error:
        db_connection.rollback()
        raise HTTPException(status_code=400, detail="Product not found or out of stock")

    finally:
        db_pool.putconn(db_connection)


@app.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: str):
    assert db_pool is not None

    db_connection = db_pool.getconn()

    try:
        product_order = get_order_service(
            GetOrderInput(connection=db_connection, order_id=order_id)
        )

        if product_order is not None:
            replenished_stock = product_order.count
            product_id = product_order.product_id

            update_product_service(
                UpdateProductInput(
                    connection=db_connection,
                    stock_offset=replenished_stock,
                    product_id=product_id,
                )
            )
            update_order_service(
                UpdateOrderInput(connection=db_connection, order_id=order_id)
            )

            db_connection.commit()

            return {"message": "ok"}

        else:
            raise HTTPException(
                status_code=400, detail="Unable to cancel product order"
            )

    except psycopg2.Error:
        db_connection.rollback()
        raise HTTPException(status_code=400, detail="Unable to cancel product order")

    finally:
        db_pool.putconn(db_connection)
