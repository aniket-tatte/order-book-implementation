from fastapi import FastAPI
from app.api.socket import socketRouter

app = FastAPI()
app.include_router(socketRouter, prefix='/api/v1/socket', tags=['web_socket_service'])
