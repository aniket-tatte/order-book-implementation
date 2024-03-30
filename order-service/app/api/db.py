import os
from sqlalchemy import (Column, DateTime, Integer, MetaData, String, Table, create_engine, Enum, Numeric, TIMESTAMP)
from sqlalchemy.sql import func
from databases import Database
from app.api.models import OrderSide, OrderStatus

DATABASE_URI = os.getenv('DATABASE_URI')

engine = create_engine(DATABASE_URI)
metadata = MetaData()

orders = Table(
    'orders',
    metadata,
    Column('order_id', String, primary_key=True),
    Column('quantity', Integer),
    Column('price', Numeric(precision=10, scale=2)),
    Column('order_side', Enum(OrderSide)),
    Column('client_id', String),
    Column('order_status', Enum(OrderStatus), default=lambda: OrderStatus.PENDING.value),
    Column('created_at', TIMESTAMP, server_default=func.current_timestamp()),
    Column('updated_at', TIMESTAMP, server_default=func.current_timestamp())
)

database = Database(DATABASE_URI)