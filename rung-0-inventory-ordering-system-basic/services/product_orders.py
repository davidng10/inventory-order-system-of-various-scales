from dataclasses import dataclass
import uuid

from services.common import ServiceBase, get_cursor


@dataclass
class GetOrderInput(ServiceBase):
    order_id: str


@dataclass
class GetOrderResult:
    product_id: uuid.UUID
    count: int


def get_order_service(args: GetOrderInput):
    order_id = args.order_id

    cursor = get_cursor(args)

    sql = """
        SELECT product_id, count from product_order WHERE cancelled = false AND id = %s
    """

    payload = (order_id,)

    cursor.execute(sql, payload)
    data = cursor.fetchone()
    if data is None:
        return None

    return GetOrderResult(product_id=data["product_id"], count=data["count"])


@dataclass
class GetOrdersInput(ServiceBase):
    user_id: str
    limit: int | None
    offset: int | None


def get_orders_service(args: GetOrdersInput):
    user_id = args.user_id
    limit = args.limit
    offset = args.offset

    cursor = get_cursor(args)

    sql = """
        SELECT *
        FROM product_order
        WHERE user_id = %s
        ORDER BY id ASC
        LIMIT %s OFFSET %s
    """

    payload = (user_id, limit, offset)

    cursor.execute(sql, payload)
    data = cursor.fetchall()

    return data


@dataclass
class CreateOrderInput(ServiceBase):
    product_id: str
    user_id: str
    product_count: int


def create_order_service(args: CreateOrderInput):
    product_id = args.product_id
    user_id = args.user_id
    product_count = args.product_count

    cursor = get_cursor(args)

    sql = """
        INSERT INTO product_order (product_id, user_id, count)
        VALUES (%s, %s, %s)
        RETURNING id;
    """

    payload = (product_id, user_id, product_count)

    cursor.execute(sql, payload)

    data = cursor.fetchone()

    return data


@dataclass
class UpdateOrderInput(ServiceBase):
    order_id: str


def update_order_service(args: UpdateOrderInput):
    order_id = args.order_id

    cursor = get_cursor(args)

    sql = """
        UPDATE product_order
        SET cancelled = true
        WHERE id = %s
    """

    payload = (order_id,)

    cursor.execute(sql, payload)
