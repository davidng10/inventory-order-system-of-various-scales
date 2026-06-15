from contextlib import asynccontextmanager

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import uuid

psycopg2.extras.register_uuid()

db_connection = None
cur = None

sample_product_id = ["019ec67f-a502-7f48-a1e3-7b2fd4d62f4a", "019ec67f-a503-701d-a0d0-6972bde610b0"]
sample_user_id = "019ec67f-a502-7dbb-8dad-74e16ac913d7"

class ProductOrderRequest(BaseModel):
    product_id: uuid.UUID
    user_id: uuid.UUID
    count: int

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_connection
    global cur

    print("Server is starting up...")
    db_connection = psycopg2.connect(
        host="localhost",
        dbname="inventory-order-sys",
        user="postgres",
        password="postgres",
        port=5432
        )
    cur = db_connection.cursor()
    
    yield  # The app serves requests while paused here
    
    # --- Shutdown Callback Logic ---
    print("Application is shutting down...")
    print("Disconnecting from DB...")
    db_connection.close()
    # Your cleanup callbacks go here (e.g., closing sessions, freeing memory)



app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    print("OK")
    return {"message": "Hello World"}


@app.post("/order")
async def create_order(orderRequest: ProductOrderRequest):
    print("Order request received");
    product_order_dict = orderRequest.model_dump()


    cur.execute("""
        SELECT * from products WHERE id = %s
    """, (product_order_dict["product_id"],))
    data = cur.fetchone()

    if (data):
        order_data = (product_order_dict["product_id"], product_order_dict["user_id"], product_order_dict["count"])
        cur.execute("""
            INSERT INTO product_order (product_id, user_id, count)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, order_data)
        product_order_item = cur.fetchone()
        db_connection.commit()
        print(product_order_item);
        return {"data": "ok"}


    else:
        raise HTTPException(status_code=404, detail="Product not found")
    
