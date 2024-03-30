from fastapi import FastAPI
import uvicorn
from app.api.order_book import orderBookRouter
from app.api.trade import tradeRouter
from app.api.db import metadata, database, engine

metadata.create_all(engine)

async def cleanDatabase():
    connection = engine.connect()
    transaction = connection.begin()
    for table in metadata.sorted_tables:
        connection.execute(table.delete())
    transaction.commit()

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await cleanDatabase()
    await database.disconnect()

app.include_router(orderBookRouter, prefix='/api/v1/order_book', tags=['order_book'])

app.include_router(tradeRouter, prefix='/api/v1/trade', tags=['trades'])

