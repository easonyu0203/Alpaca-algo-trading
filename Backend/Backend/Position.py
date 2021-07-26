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
position_url = f'{base_url}/v2/positions'
        
class Position:
    def __init__(self, **kwarg) -> None:
        self.info = kwarg
        self.symbol = kwarg['symbol']
        self.exchange = kwarg['exchange']
        self.avg_entry_price = kwarg['avg_entry_price']
        self.qty = kwarg['qty']
        self.side = kwarg['side']
        self.market_value = kwarg['market_value']
        self.unrealized_pl = kwarg['unrealized_pl']
        self.unrealized_plpc = kwarg['unrealized_plpc']
        self.unrealized_intraday_pl = kwarg['unrealized_intraday_pl']
        self.unrealized_intraday_plpc = kwarg['unrealized_intraday_plpc']
        self.current_price = kwarg['current_price']
        self.lastday_price = kwarg['lastday_price']
        self.change_today = kwarg['change_today']
    
    def get_all_open_position() -> List:
        '''
        get  all open position
        return dict of Position object with index by symbol
        '''
        url = position_url
        r = requests.get(url, headers=authentication_header)
        r.raise_for_status()
        positions = [Position(**i) for i in json.loads(r.content)]
        out_dict = dict()
        for p in positions:
            out_dict[p.symbol] = p
        return out_dict

    def get_open_position(symbol):
        '''
        get position of 'symbol'
        return Position object or 'None' if don't have this symbol position 
        '''
        url = f'{position_url}/{symbol}'
        r = requests.get(url, headers=authentication_header)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
        data = json.loads(r.content)
        return Position(**data)
    
    def close_all_position():
        '''
        close all position
        '''
        url = position_url
        r = requests.delete(url, headers=authentication_header, params={'cancel_orders': True})
        r.raise_for_status()
    
    def close_position(symbol):
        '''
        close this position
        '''
        url = f'{position_url}/{symbol}'
        params = {
            'percentage': 100,
        }
        r = requests.delete(url, headers=authentication_header, params=params)
        r.raise_for_status()
    
    def _process_alpaca_position(positions):
        out_dict = dict()
        for p in positions:
            out_dict[p.symbol] = p
        return out_dict
    
    def __repr__(self) -> str:
        return str(self.info)

if __name__ == '__main__':
    Position.close_all_position()