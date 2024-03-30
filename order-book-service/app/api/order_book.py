from fastapi import APIRouter, HTTPException
from app.api.models import Order, OrderBook

orderBookRouter = APIRouter()
orderBookService = OrderBook()

@orderBookRouter.post('/addOrderToOrderBook')
async def addOrderToOrderBook(payload: Order):
    payload = payload.dict()
    await orderBookService.executeOrder(payload)
    return {
        'response': f"Added order_id: {payload['order_id']} to the order book"
    }

@orderBookRouter.get('/getOrderBookSnapshot')
def getOrderBookSnapshot():
    return orderBookService.getOrderBookSnapshot()

@orderBookRouter.post('/removeOrderFromOrderBook')
async def removeOrderFromOrderBook(payload: Order):
    payload = payload.dict()
    print(payload)
    orderBookService.removeOrderFromOrderBook(payload, payload['quantity'])
    return {
        'response': f"Order_id: {payload['order_id']} marked as cancelled"
    }
