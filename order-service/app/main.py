from fastapi import FastAPI
from app.api.orders import orders
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
    print('Cleaning database before Shutting Down')
    await cleanDatabase()
    await database.disconnect()

app.include_router(orders, prefix='/api/v1/orders', tags=['orders'])