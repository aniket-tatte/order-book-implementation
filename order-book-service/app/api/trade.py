from fastapi import APIRouter, HTTPException
from app.api import db_manager
from app.api.models import OrderSide, Order

tradeRouter = APIRouter()

@tradeRouter.get('/getAllTrades')
async def getAllTrades():
    return await db_manager.getAllTrades()

@tradeRouter.post('/getTradeDataByOrder')
async def getTradeDataByOrder(order: Order):
    order = order.dict()
    columnName = ''
    if order['order_side']==OrderSide.BUY:
        columnName = 'bid_order_id'
    else:
        columnName = 'ask_order_id'
    records = await db_manager.getTradeDataByOrderId(order['order_id'], columnName)
    return [dict(record) for record in records]
