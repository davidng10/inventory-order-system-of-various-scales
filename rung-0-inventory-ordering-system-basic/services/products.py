
from dataclasses import dataclass

import uuid

from services.common import ServiceBase, get_cursor

@dataclass
class UpdateProductStockInput(ServiceBase):
    stock: int
    product_id: uuid.UUID

@dataclass
class UpdateProductStockOutput:
    success: bool

def update_product_stock(args: UpdateProductStockInput) -> UpdateProductStockOutput:
    connection = args.connection, stock=args.stock, product_id=args.product_id

    cursor = get_cursor(args)

    update_product_stock_sql = """
        UPDATE products
        SET stock = stock - %s
        WHERE id = %s
    """

    update_product_stock_payload = (stock, product_id)

    cursor.execute(update_product_stock_sql, update_product_stock_payload)

    updated_count = cursor.rowcount

    return UpdateProductStockOutput(success=updated_count > 0)