import enum
from pydantic import BaseModel, Field, validator
import heapq
from collections import deque
from app.api import db_manager
from app.api import service

class OrderSide(enum.IntEnum):
    BUY = 1
    SELL = -1

class Order(BaseModel):
    order_id: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0, multiple_of=0.01)
    order_side: OrderSide
    client_id: str = Field(..., min_length=5)

    @validator("order_side")
    def validate_order_side(cls, v):
        if v not in [OrderSide.BUY, OrderSide.SELL]:
            raise ValueError("order_side must be either 1 or -1")
        return v

class OrderBook():
    def __init__(self):
        self.lowestSellingPriceHeap = []
        self.highestBuyingPriceHeap = []
        # Min Heap
        heapq.heapify(self.lowestSellingPriceHeap)
        # Max Heap
        heapq._heapify_max(self.highestBuyingPriceHeap)

        # Key -> (price, order_side)
        # Value -> volume = totalQuantity
        self.volumeMap = dict()

        # Key -> (price, order_side)
        # Value -> reference to the queue in heap
        self.queueMap = dict()
    
    def __getOrderData(self, order_id: str):
        # TODO -> Get order data from order service
        pass
    
    def __getOppositeSideOfOrder(self, order: Order):
        # Return the opposite of order_side
        return OrderSide.BUY if order['order_side'] == OrderSide.SELL else OrderSide.SELL

    async def executeOrder(self, order:Order):
        # Run the matching algorithm for incoming order and add the order to order book if not traded completely
        originalOrderQuantity = order['quantity']
        oppositeOrderSide = self.__getOppositeSideOfOrder(order)
        oppositeOrderSideHeap = self.lowestSellingPriceHeap if oppositeOrderSide == OrderSide.SELL else self.highestBuyingPriceHeap
        while (order["quantity"] > 0) and (len(oppositeOrderSideHeap) > 0):
            if (oppositeOrderSide==OrderSide.SELL and oppositeOrderSideHeap[0][0] <= order['price']) or (oppositeOrderSide==OrderSide.BUY and oppositeOrderSideHeap[0][0] >= order['price']):
                matchingOrder = oppositeOrderSideHeap[0][1][0]
                tradePrice = matchingOrder['price']
                tradeQuantity = min(matchingOrder['quantity'], order['quantity'])
                matchingOrder['quantity']-=tradeQuantity
                order['quantity']-=tradeQuantity
                trade = self.__createTradeObject(order, matchingOrder, tradePrice, tradeQuantity)
                trade_id = await db_manager.createTrade(trade)
                trade['trade_id'] = trade_id
                await service.sendTradeUpdate(trade)
                if matchingOrder['quantity']==0:
                    self.removeOrderFromOrderBook(matchingOrder, tradeQuantity)
                    service.markOrderAsComplete(matchingOrder['order_id'])
                    print(f'mark order {matchingOrder["order_id"]} complete')
                else:
                    if tradeQuantity>0:
                        service.markOrderAsProcessing(matchingOrder['order_id'])  
                    self.volumeMap[(matchingOrder['price'], matchingOrder['order_side'])] = max(0, self.volumeMap[(matchingOrder['price'], matchingOrder['order_side'])] - tradeQuantity)
            else:
                break

        if order['quantity'] > 0:
            if order['quantity'] < originalOrderQuantity:
                service.markOrderAsProcessing(order['order_id'])
            self.addOrderToOrderBook(order)
        else:
            service.markOrderAsComplete(order['order_id'])
    
    def addOrderToOrderBook(self, order: Order):
        if (order['price'], order['order_side']) not in self.queueMap:
            self.queueMap[(order['price'], order['order_side'])] = deque([order])
            self.volumeMap[(order['price'], order['order_side'])] = order['quantity']
            if order['order_side']==OrderSide.SELL:
                heapq.heappush(self.lowestSellingPriceHeap, (order['price'], self.queueMap[(order['price'], order['order_side'])]))
            else:
                self.highestBuyingPriceHeap.append((order['price'], self.queueMap[(order['price'], order['order_side'])]))
                heapq._heapify_max(self.highestBuyingPriceHeap)

        else:
            self.queueMap[(order['price'], order['order_side'])].append(order)
            self.volumeMap[(order['price'], order['order_side'])] += order['quantity']
    
    def removeOrderFromOrderBook(self, order: Order, tradeQuantity: int):
        priceQueue = self.queueMap[(order['price'], order['order_side'])]
        priceQueue.remove(order)
        if len(priceQueue)==0:
            if order['order_side']==OrderSide.SELL:
                self.lowestSellingPriceHeap.remove((order['price'], priceQueue))
                heapq.heapify(self.lowestSellingPriceHeap)
            else:
                self.highestBuyingPriceHeap.remove((order['price'], priceQueue))
                heapq._heapify_max(self.highestBuyingPriceHeap)
        self.volumeMap[(order['price'], order['order_side'])]-=tradeQuantity
        # if (self.volumeMap[(order['price'], order['order_side'])]) == 0:
        #     del self.volumeMap[(order['price'], order['order_side'])]

    def getOrderBookSnapshot(self, depth = 5):
        response = {
            'buySide': [],
            'sellSide': []
        }
        for (price, order_side), quantity in self.volumeMap.items():
            if order_side == OrderSide.BUY:
                response['buySide'].append({
                    'price': price,
                    'quantity': quantity
                })
            else:
                response['sellSide'].append({
                    'price': price,
                    'quantity': quantity
                })
        response['buySide'] = sorted(response["buySide"], key=lambda x: x["price"])
        response["sellSide"] = sorted(response["sellSide"], key=lambda x: x["price"])
        return response
    
    def __createTradeObject(self, order: Order, matchingOrder: Order, tradePrice: float, tradeQuantity: int):
        trade = {
            'price': tradePrice,
            'quantity': tradeQuantity
        }
        if order['order_side']==OrderSide.BUY:
            trade['bid_order_id'] = order['order_id']
            trade['ask_order_id'] = matchingOrder['order_id']
        else:
            trade['bid_order_id'] = matchingOrder['order_id']
            trade['ask_order_id'] = order['order_id']
        
        return trade

class Trade(BaseModel):
    trade_id: str = Field(..., min_length=1)
    price: float = Field(..., gt=0, multiple_of=0.01)
    quantity: int = Field(..., gt=0)
    bid_order_id: str = Field(..., min_length=1)
    ask_order_id: str = Field(..., min_length=1)

    @validator('trade_id', 'bid_order_id', 'ask_order_id')
    def check_empty_string(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v