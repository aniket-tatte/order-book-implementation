import enum
from pydantic import BaseModel, Field, validator
from typing import Optional

class OrderSide(enum.IntEnum):
    BUY = 1
    SELL = -1

class OrderStatus(str, enum.Enum):
    PENDING = 'Pending'
    COMPLETED = 'Completed'
    CANCELLED = 'Cancelled'

class CreateOrderRequest(BaseModel):
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0, multiple_of=0.01)
    order_side: OrderSide
    client_id: str = Field(..., min_length=5)

    @validator("order_side")
    def validate_order_side(cls, v):
        if v not in [OrderSide.BUY, OrderSide.SELL]:
            raise ValueError("order_side must be either 1 or -1")
        return v

class UpdateOrderRequest(BaseModel):
    order_id: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0, multiple_of=0.01)

class UpdateOrderStatusRequest(BaseModel):
    order_id: str
    order_status: OrderStatus

class OrderResponse(BaseModel):
    order_id: str
    quantity: int 
    price: float
    order_side: OrderSide
    order_status: Optional[OrderStatus]
    client_id: str
    average_traded_price: Optional[float] = None
    traded_quantity: Optional[int] = None
    order_alive: Optional[bool] = None