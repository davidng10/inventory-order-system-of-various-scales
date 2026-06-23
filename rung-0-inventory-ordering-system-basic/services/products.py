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


def update_product_stock_service(
    args: UpdateProductStockInput,
) -> UpdateProductStockOutput:
    stock = args.stock
    product_id = args.product_id

    cursor = get_cursor(args)

    update_product_stock_sql = """
        UPDATE products
        SET stock = stock - %s
        WHERE id = %s AND stock >= %s
    """

    update_product_stock_payload = (stock, product_id, stock)

    cursor.execute(update_product_stock_sql, update_product_stock_payload)

    updated_count = cursor.rowcount

    return UpdateProductStockOutput(success=updated_count > 0)


@dataclass
class GetProductStockInput(ServiceBase):
    product_id: uuid.UUID


@dataclass
class GetProductStockOutput:
    stock: int


def get_product_stock_service(
    args: GetProductStockInput,
) -> GetProductStockOutput | None:
    product_id = args.product_id

    cursor = get_cursor(args)

    sql = """
        SELECT stock
        FROM products
        WHERE id = %s
    """

    payload = (product_id,)

    cursor.execute(sql, payload)

    data = cursor.fetchone()

    if data is None:
        return None

    return GetProductStockOutput(stock=data["stock"])


@dataclass
class UpdateProductInput(ServiceBase):
    stock_offset: int
    product_id: uuid.UUID


def update_product_service(args: UpdateProductInput):
    stock_offset = args.stock_offset
    product_id = args.product_id

    cursor = get_cursor(args)

    sql = """
        UPDATE products
        SET stock = stock + %s
        WHERE id = %s
    """

    payload = (stock_offset, product_id)

    cursor.execute(sql, payload)
