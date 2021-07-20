from typing import List
import requests
import json
from datetime import datetime
import os
import pandas as pd
import pyrfc3339
from dotenv import load_dotenv; load_dotenv()
from config import USATimeZone

from account import getAccountInfo

authentication_header = {
    'APCA-API-KEY-ID': os.environ.get('APCA-API-KEY-ID'),
    'APCA-API-SECRET-KEY': os.environ.get('APCA-API-SECRET-KEY')
}

base_url = os.environ.get('APCA_API_BASE_URL')
order_url = f'{base_url}/v2/orders'


class Order:
    def __init__(self, **kwarg) -> None:
        self.info_dict = kwarg

    def __repr__(self) -> str:
        return str(self.info_dict)

def get_all_order():
    r = requests.get(order_url, headers=authentication_header)
    r.raise_for_status()
    orders = json.loads(r.content)
    return orders

def simple_order(ticker, dollar_amount):
    '''
    place a market day order for 'ticker' for 'dollar_amount'
    '''
    side = 'buy' if dollar_amount >= 0 else 'sell'

    body_para = json.dumps({
        'symbol': ticker,
        'notional': dollar_amount,
        'side': side,
        'type': 'market',
        'time_in_force': 'day',
    })
    r = requests.post(order_url, headers=authentication_header, data=body_para)
    r.raise_for_status()
    _order = Order(**json.loads(r.content))
    return _order

def cancel_orders(order_ids: List=None):
    '''
    cancel all order if no id provide, else cancel list of order provide by order_ids
    '''
    if order_ids is None:
        url = order_url
        r = requests.delete(url, headers=authentication_header)
        r.raise_for_status()
    else:
        for id in order_ids:
            url = f'{order_url}/{id}'
            r = requests.delete(url, headers=authentication_header)
            r.raise_for_status()


if __name__ == '__main__':
    order = simple_order('TSLA', 1000)

    print(order)