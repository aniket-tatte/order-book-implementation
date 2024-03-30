import os
import requests

WEB_SOCKET_SERVICE_BASE_URL = os.getenv('WEB_SOCKET_SERVICE_BASE_URL')
ORDER_SERIVCE_BASE_URL = os.getenv('ORDER_SERIVCE_BASE_URL')

async def sendTradeUpdate(trade):
    url = f'''{WEB_SOCKET_SERVICE_BASE_URL}/api/v1/socket/sendTradeUpdate'''
    try:
        response = requests.post(url, json=trade)
        if response.status_code > 399:
            print(trade)
            print(response)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while sending trade update: {e}")

async def markOrderAsComplete(order_id: str):
    url = f'''{ORDER_SERIVCE_BASE_URL}/api/v1/orders/updateOrderStatus'''
    try:
        response = requests.post(url, json={
            'order_id': order_id,
            'order_status': 'Completed'
        })
        if response.status_code > 399:
            print(order_id)
            print(response)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while marking trade as complete: {e}")