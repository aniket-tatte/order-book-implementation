from typing import List
from fastapi import APIRouter, HTTPException
import app.api.service as service
from app.api.models import CreateOrderRequest, OrderResponse, OrderStatus, UpdateOrderStatusRequest
from app.api import db_manager

orders = APIRouter()

@orders.post('/', status_code=201, response_model=OrderResponse)
async def createOrder(payload: CreateOrderRequest):
    order_id = await db_manager.createOrder(payload)
    order = {
        'order_id': order_id,
        'order_status': OrderStatus.PENDING,
        **payload.dict(),
    }
    await service.addOrderToOrderBook(order)
    return order

@orders.get('/', response_model=List[OrderResponse])
async def getAllOrders():
    return await db_manager.getAllOrders()

@orders.get('/{order_id}/', response_model=OrderResponse)
async def getOrder(order_id: str):
    order = await db_manager.getOrder(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order = dict(order)
    order['price'] = float(order['price'])
    order['created_at'] = str(order['created_at'])
    order['updated_at'] = str(order['updated_at'])
    trades = service.getTradeDataByOrder(order)
    total_traded_price, traded_quantity = float(0), int(0)
    for trade in trades:
        total_traded_price+=(trade['price'] * trade['quantity'])
        traded_quantity+=trade['quantity']
    order['average_traded_price'] = float(0) if (traded_quantity==0) else (total_traded_price / traded_quantity)
    order['traded_quantity'] = traded_quantity
    order['order_alive'] = not (traded_quantity == order['quantity'])
    return order

@orders.delete('/{order_id}/', response_model=None)
async def deleteOrder(order_id: str):
    order = await db_manager.getOrder(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.order_status != OrderStatus.PENDING:
        raise HTTPException(status_code=404, detail=f"Order can not be cancelled order_status - {order.order_status}")
    order = dict(order)
    order['price'] = float(order['price'])
    order['created_at'] = str(order['created_at'])
    order['updated_at'] = str(order['updated_at'])
    service.removeOrderFromOrderBook(order)
    payload: UpdateOrderStatusRequest = {
        'order_id': order_id,
        'order_status': OrderStatus.CANCELLED
    }
    return await db_manager.updateOrderStatus(payload)

@orders.post('/updateOrderStatus')
async def updateOrderStatus(payload: UpdateOrderStatusRequest):
    payload = payload.dict()
    order = await db_manager.getOrder(payload['order_id'])
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.order_status != OrderStatus.PENDING:
        raise HTTPException(status_code=404, detail=f"Order Status can not be updated order_status {order.order_status}")
    return await db_manager.updateOrderStatus(payload)