import os
import requests

ORDER_BOOK_SERVICE_BASE_URL = os.getenv('ORDER_BOOK_SERVICE_BASE_URL')

def getOrderBookData():
    url = f'''{ORDER_BOOK_SERVICE_BASE_URL}/api/v1/order_book/getOrderBookSnapshot'''
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get Order Book Snapshot. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while getting Order Book Snapshot: {e}")