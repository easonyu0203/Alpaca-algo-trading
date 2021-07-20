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
position_url = f'{base_url}/v2/positions'

def get_open_position(tickers:List=None) -> List:
    '''
    get all open position if 'ticker' not provide else get open position of this ticker
    return [] if no position is open or don't have this ticker position 
    '''
    url = position_url
    r = requests.get(url, headers=authentication_header)
    r.raise_for_status()
    positions = [Position(**i) for i in json.loads(r.content)]
    if tickers is not None:
        positions = [i for i in positions if i.info['symbol'] in tickers]
    return positions

def close_position(tickers:List=None):
    '''
    close all position and order if no 'tickers' else close 'tickers' position
    '''
    if tickers is None:
        url = position_url
        r = requests.delete(url, headers=authentication_header, params={'cancel_orders': True})
        r.raise_for_status()
    else:
        assert type(tickers) == List
        for ticker in tickers:
            url = f'{position_url}/{ticker}'
            params = {
                'symbol': ticker,
                'percentage': 100,
            }
            r = requests.delete(url, headers=authentication_header, params=params)
            r.raise_for_status()

class Position:
    def __init__(self, **kwarg) -> None:
        self.info = kwarg
    
    def __repr__(self) -> str:
        return str(self.info)

if __name__ == '__main__':
    # print(get_open_position())
    url = f'{base_url}/v2/assets'
    