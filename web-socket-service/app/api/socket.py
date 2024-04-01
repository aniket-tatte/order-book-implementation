import json
import asyncio
import starlette
import websockets
from fastapi import APIRouter, WebSocket
from app.api.service import getOrderBookData
from typing import List
from app.api.models import Trade
from collections import deque

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message):
        for connection in self.active_connections:
            await connection.send_json(message)

socketRouter = APIRouter()
manager = ConnectionManager()

async def sendOrderBookData(websocket):
    while True:
        try:
            data = getOrderBookData()
            await websocket.send_json(data)
            await asyncio.sleep(1)
        except starlette.websockets.WebSocketDisconnect:
            break

@socketRouter.websocket('/getOrderBookSnapshot')
async def getOrderBookSnapshot(websocket: WebSocket):
    await websocket.accept()
    await sendOrderBookData(websocket)

@socketRouter.post('/sendTradeUpdate')
async def sendTradeUpdate(payload: Trade):
    print(payload)
    await manager.broadcast(payload.dict())

@socketRouter.websocket('/getTradeUpdate')
async def getTradeUpdate(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except starlette.websockets.WebSocketDisconnect:
        manager.disconnect(websocket)

