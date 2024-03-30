import uuid
from app.api.models import CreateOrderRequest, UpdateOrderRequest, OrderStatus, UpdateOrderStatusRequest
from app.api.db import orders, database

async def createOrder(payload: CreateOrderRequest):
    order_id = uuid.uuid4().hex
    query = orders.insert().values({
        'order_id': order_id,
        'order_status': OrderStatus.PENDING,
        **payload.dict()
    })
    await database.execute(query=query)
    return order_id

async def getAllOrders():
    query = orders.select()
    return await database.fetch_all(query=query)

async def getOrder(order_id: str):
    query = orders.select().where(orders.c.order_id == order_id)
    return await database.fetch_one(query=query)

async def deleteOrder(order_id: str):
    query = orders.delete().where(orders.c.order_id==order_id)
    return await database.execute(query=query)

async def updateOrder(order_id: str, payload: UpdateOrderRequest):
    query = (
        orders
        .update()
        .where(orders.c.order_id == order_id)
        .values(**payload.dict())
    )
    return await database.execute(query=query)

async def updateOrderStatus(payload: UpdateOrderStatusRequest):
    query = (
        orders
        .update()
        .where(orders.c.order_id == payload['order_id'])
        .values(**payload)
    )
    return await database.execute(query=query)
