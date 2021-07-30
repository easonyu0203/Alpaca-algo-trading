from logging import info
import requests
import json
import os
from dotenv import load_dotenv; load_dotenv()

authentication_header = {
    'APCA-API-KEY-ID': os.environ.get('APCA-API-KEY-ID'),
    'APCA-API-SECRET-KEY': os.environ.get('APCA-API-SECRET-KEY')
}

class Account:
    '''
    information of the account, 
    every time getting a property of account is doing a http request to Aplaca API,
    so don't call too many time, else the program will be every slow
    '''
    def __init__(self) -> None:
        # self._update()
        pass
    
    def _update(self) -> None:
        info_dict = self._getAccountInfo()
        self._info_dict = info_dict
        self._cash = float(info_dict['cash'])
        self._buying_power = float(info_dict['buying_power'])
        # self._regt_buying_power = info_dict['regt_buying_power']
        # self._daytrading_buying_power = info_dict['daytrading_buying_power']
        self._pattern_day_trader = bool(info_dict['pattern_day_trader'])
        self._equity = float(info_dict['equity'])
        # self._last_equity = info_dict['last_equity']
        self._long_market_value = float(info_dict['long_market_value'])
        self._short_market_value = float(info_dict['short_market_value'])
        # self._initial_margin = info_dict['initial_margin']
        # self._maintenance_margin = info_dict['maintenance_margin']
        # self._last_maintenance_margin = info_dict['last_maintenance_margin']
        self._daytrade_count = int(info_dict['daytrade_count'])

        assert self._short_market_value == 0
        # assert self._pattern_day_trader == False
    
    def _getAccountInfo(self) -> dict:
        '''
        Get account informations
        return dictionary
        '''
        base_url = os.environ.get('APCA_API_BASE_URL')
        account_url = f'{base_url}/v2/account'
        r = requests.get(account_url, headers=authentication_header)
        r.raise_for_status()
        account_info = json.loads(r.content)
        return account_info
    
    @property
    def info_dict(self):
        self._update()
        return self._info_dict

    @property
    def cash(self):
        self._update()
        return self._cash
    
    @property
    def buying_power(self):
        self._update()
        return self._buying_power
    
    @property
    def equity(self):
        self._update()
        return self._equity
    

    def __repr__(self) -> str:
        return str(self._info_dict)




def main():
    # info = getAccountInfo()
    myAccount = Account()
    print(myAccount.buying_power)
    


if __name__ == '__main__':
    main()

