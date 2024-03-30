import uuid
from app.api.db import trades, database

async def createTrade(payload: {
    'price': float,
    'quantity': int,
    'bid_order_id': str,
    'ask_order_id': str
}):
    trade_id = uuid.uuid4().hex
    query = trades.insert().values({
        'trade_id': trade_id,
        **payload
    })
    await database.execute(query=query)
    return trade_id

async def getAllTrades():
    query = trades.select()
    return await database.fetch_all(query=query)

async def getTrade(trade_id: str):
    query = trades.select().where(trades.c.trade_id == trade_id)
    return await database.fetch_one(query=query)

async def getTradeDataByOrderId(order_id: str, columnName: str):
    column = getattr(trades.c, columnName)
    query = trades.select().where(column == order_id)
    return await database.fetch_all(query)


