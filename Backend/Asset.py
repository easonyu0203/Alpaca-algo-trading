from typing import List
import requests
import json
import os
from dotenv import load_dotenv; load_dotenv()
from config import USATimeZone

authentication_header = {
    'APCA-API-KEY-ID': os.environ.get('APCA-API-KEY-ID'),
    'APCA-API-SECRET-KEY': os.environ.get('APCA-API-SECRET-KEY')
}

base_url = os.environ.get('APCA_API_BASE_URL')
asset_url = f'{base_url}/v2/assets'

class Asset:
    def __init__(self, **kwarg) -> None:
        self.info = kwarg

    def __repr__(self) -> str:
        return str(self.info)

def get_asset(tickers:List=None) -> List:
    '''
    get list of all assets if 'tickers' not provide or only list of asset in 'tickers'
    '''
    url = asset_url
    r = requests.get(url, headers=authentication_header)
    r.raise_for_status()
    assets = [Asset(**i) for i in json.loads(r.content)]
    if tickers is not None:
        assets = [i for i in assets if i.info['symbol'] in tickers]
        assert len(tickers) == len(assets) #if not that mean some ticker can't be found
    return assets

if __name__ == '__main__':
    tickers = ['GOOGL']
    all_assets = get_asset(tickers)
    print(all_assets)