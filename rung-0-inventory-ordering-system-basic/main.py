from contextlib import asynccontextmanager
from typing import Annotated

import psycopg2
import psycopg2.extras
from psycopg2 import pool
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

import uuid

psycopg2.extras.register_uuid()

db_pool = None

class CreateProductOrderRequest(BaseModel):
    product_id: uuid.UUID
    user_id: uuid.UUID
    count: int

class CommonHeaders(BaseModel):
    x_user_id: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool

    print("Server is starting up...")

    db_pool = pool.ThreadedConnectionPool(2, 10,
        host="localhost",
        dbname="inventory-order-sys",
        user="postgres",
        password="postgres",
        port=5432
        )
    
    yield  # The app serves requests while paused here
    
    # --- Shutdown Callback Logic ---
    print("Application is shutting down...")
    print("Disconnecting from DB...")
    db_pool.closeall()
    # Your cleanup callbacks go here (e.g., closing sessions, freeing memory)



app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root(headers: Annotated[CommonHeaders, Header()]):
    print(dict(headers))
    return {"message": "git gud"}

@app.get("/product/{product_id}/stock")
async def get_product_stock(product_id: str):
    get_product_stock_sq = """
        SELECT stock
        FROM products
        WHERE id = %s
    """

    db_connection = db_pool.getconn()

    try:
        cur = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(get_product_stock_sq, (product_id,))
        data = cur.fetchone()

        return {"data": data}

    except psycopg2.Error as e:
        db_connection.rollback()
        raise HTTPException(status_code=400, detail="Unable to get product stock")

    finally:
        db_pool.putconn(db_connection)

    
    
@app.get("/orders")
async def get_orders(headers: Annotated[CommonHeaders, Header()], limit: int = 10, offset: int = 0):

    header_dict = dict(headers)
    user_id = header_dict["x_user_id"];

    db_connection = db_pool.getconn()

    try:
        cur = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        get_orders_sql = """
            SELECT *
            FROM product_order
            WHERE user_id = %s
            ORDER BY id ASC
            LIMIT %s OFFSET %s
        """

        cur.execute(get_orders_sql, (user_id, limit, offset))
        data = cur.fetchall()

        return {"data": data}
    except psycopg2.Error as e:
        db_connection.rollback()
        raise HTTPException(status_code=400, detail="Unable to get product order")
    finally:
        db_pool.putconn(db_connection)


@app.post("/orders")
async def create_order(request: CreateProductOrderRequest):
    product_order_dict = request.model_dump()
    db_connection = db_pool.getconn()

    try:
        get_valid_products_sql = """
           SELECT * from products WHERE id = %s AND stock >= %s
        """
            
        cur = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(get_valid_products_sql, (product_order_dict["product_id"], product_order_dict["count"] ))
        data = cur.fetchone()

        if data is not None:
            order_data = (product_order_dict["product_id"], product_order_dict["user_id"], product_order_dict["count"])
            create_order_sql = """
                INSERT INTO product_order (product_id, user_id, count)
                VALUES (%s, %s, %s)
                RETURNING id;
            """
            cur.execute(create_order_sql, order_data)
            product_order_item = cur.fetchone()

            update_product_stock_data = data["stock"] - product_order_dict["count"]

            update_product_stock_sql = """
                UPDATE products
                SET stock = %s
                WHERE id = %s
            """
            cur.execute(update_product_stock_sql, (update_product_stock_data, product_order_dict["product_id"]))
            db_connection.commit()

            return {"data": product_order_item}

        else:
            raise HTTPException(status_code=400, detail="Product not found or out of stock")
        
    except psycopg2.Error as e:
        db_connection.rollback()
        raise HTTPException(status_code=400, detail="Product not found or out of stock")
    finally:
        db_pool.putconn(db_connection)



@app.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: str):
    get_order_sql = """
        SELECT product_id, count from product_order WHERE cancelled = false AND id = %s
    """

    db_connection = db_pool.getconn()

    try:
        cur = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(get_order_sql, (order_id,))
        product_order = cur.fetchone()

        if product_order is not None:
            replenished_stock = product_order["count"]
            product_id = product_order["product_id"]

            update_products_sql = """
                UPDATE products
                SET stock = stock + %s
                WHERE id = %s
            """

            update_product_order_sql = """
                UPDATE product_order
                SET cancelled = true
                WHERE id = %s
            """

            cur.execute(update_products_sql, (replenished_stock, product_id))
            cur.execute(update_product_order_sql, (order_id,))

            db_connection.commit()

            return {"message": "ok"}

        else:
            raise HTTPException(status_code=400, detail="Unable to cancel product order")
     
    except psycopg2.Error as e:
        db_connection.rollback()
        raise HTTPException(status_code=400, detail="Unable to cancel product order")
    
    finally:
        db_pool.putconn(db_connection)
