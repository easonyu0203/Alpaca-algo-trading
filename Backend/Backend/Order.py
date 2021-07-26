from typing import List
import requests
import json
import os
from dotenv import load_dotenv; load_dotenv()
from .config import USATimeZone

authentication_header = {
    'APCA-API-KEY-ID': os.environ.get('APCA-API-KEY-ID'),
    'APCA-API-SECRET-KEY': os.environ.get('APCA-API-SECRET-KEY')
}

base_url = os.environ.get('APCA_API_BASE_URL')
order_url = f'{base_url}/v2/orders'


class Order:
    def __init__(self, **kwarg) -> None:
        self.info_dict = kwarg
        self.id = kwarg['id']

    def get_all_order():
        '''
        get list of all open order
        return list of Order object
        '''
        r = requests.get(order_url, headers=authentication_header)
        r.raise_for_status()
        orders = json.loads(r.content)
        return orders

    def simple_order(symbol, dollar_amount):
        '''
        place a market day order for 'symbol' for 'dollar_amount'
        return an Order ojbect
        '''
        side = 'buy' if dollar_amount >= 0 else 'sell'

        body_para = json.dumps({
            'symbol': symbol,
            'notional': dollar_amount,
            'side': side,
            'type': 'market',
            'time_in_force': 'day',
        })
        r = requests.post(order_url, headers=authentication_header, data=body_para)
        r.raise_for_status()
        _order = Order(**json.loads(r.content))
        return _order

    def cancel_all_order():
        '''
        cancel all order
        return None
        '''
        url = order_url
        r = requests.delete(url, headers=authentication_header)
        r.raise_for_status()
    
    def cancel(self):
        '''
        cancel this order
        return None
        '''
        url = f'{order_url}/{self.id}'
        r = requests.delete(url, headers=authentication_header)
        r.raise_for_status()

    def __repr__(self) -> str:
        return str(self.info_dict)




if __name__ == '__main__':
    order = Order.simple_order('TSLA', 1000)

    print(order)