import os
from sqlalchemy import (Column, DateTime, Integer, MetaData, String, Table, create_engine, Enum, Numeric, TIMESTAMP)
from sqlalchemy.sql import func
from databases import Database

DATABASE_URI = os.getenv('DATABASE_URI')

engine = create_engine(DATABASE_URI)
metadata = MetaData()

trades = Table(
    'trades',
    metadata,
    Column('trade_id', String, primary_key=True),
    Column('price', Numeric(precision=10, scale=2)),
    Column('quantity', Integer),
    Column('bid_order_id', String),
    Column('ask_order_id', String),
    Column('execution_timestamp', TIMESTAMP, server_default=func.current_timestamp())
)

database = Database(DATABASE_URI)