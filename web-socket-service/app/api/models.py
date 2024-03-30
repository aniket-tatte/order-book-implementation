from pydantic import BaseModel, Field, validator

class Trade(BaseModel):
    trade_id: str = Field(..., min_length=1)  # Ensure non-empty strings
    price: float = Field(..., gt=0, multiple_of=0.01)
    quantity: int = Field(..., gt=0)
    bid_order_id: str = Field(..., min_length=1)  # Ensure non-empty strings
    ask_order_id: str = Field(..., min_length=1)  # Ensure non-empty strings

    @validator('trade_id', 'bid_order_id', 'ask_order_id')
    def check_empty_string(cls, v):
        if not v.strip():  # Check if string is empty or contains only whitespace
            raise ValueError("Field cannot be empty")
        return v