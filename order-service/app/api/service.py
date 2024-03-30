import os
import requests
from app.api.models import OrderResponse as Order

ORDER_BOOK_SERVICE_BASE_URL = os.getenv('ORDER_BOOK_SERVICE_BASE_URL')

def addOrderToOrderBook(order: Order):
    url = f'''{ORDER_BOOK_SERVICE_BASE_URL}/api/v1/order_book/addOrderToOrderBook'''
    try:
        response = requests.post(url, json=order)
        if response.status_code == 200:
            print(f"Order with order_id {order['order_id']} added successfully")
        else:
            print(f"Failed to add order. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"order_id - {order['order_id']} An error occurred: {e}")

def getTradeDataByOrder(order: Order):
    url = f'''{ORDER_BOOK_SERVICE_BASE_URL}/api/v1/trade/getTradeDataByOrder'''
    try:
        response = requests.post(url, json=order)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to add order. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to get trade data for order_id {order['order_id']} An error occurred: {e}")

def removeOrderFromOrderBook(order: Order):
    url = f'''{ORDER_BOOK_SERVICE_BASE_URL}/api/v1/order_book/removeOrderFromOrderBook'''
    try:
        response = requests.post(url, json=order)
        if response.status_code == 200:
            print(f"Order with order_id {order['order_id']} cancelled")
        else:
            print(f"Failed to cancel order. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"order_id Cancelleation - {order['order_id']} An error occurred: {e}")
