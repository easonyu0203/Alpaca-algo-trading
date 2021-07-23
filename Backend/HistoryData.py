from logging import log
from typing import List
import requests
import os
import pandas as pd
import pyrfc3339
from datetime import datetime
from config import USATimeZone
from dotenv import load_dotenv; load_dotenv()

authentication_header = {
    'APCA-API-KEY-ID': os.environ.get('APCA-API-KEY-ID'),
    'APCA-API-SECRET-KEY': os.environ.get('APCA-API-SECRET-KEY')
}

class Resolution:
    Min = '1Min'
    Hour = '1Hour'
    Day = '1Day'
    
def getHistoryBarsData(ticker, start, end, resolution):
    '''
    Get History bars data from [start] to [end]([end] include) with [resolution] resolution,

    return pandas Dataframe with
    column=['timestape', 'open', 'high', 'low', 'close', 'volume']
    timestape is bar open timestape
    '''
    columns = ['timestape', 'open', 'high', 'low', 'close', 'volume']
    base_url = os.environ.get('APCA_API_DATA_URL')
    trade_url =  f'{base_url}/v2/stocks/{ticker}/bars'
    payload = {
        'start': pyrfc3339.generate(start),
        'end': pyrfc3339.generate(end),
        'timeframe': resolution,
        'page_token': '',
    }
    bars = []
    while(True):
        r = requests.get(trade_url, headers=authentication_header, params=payload)
        r.raise_for_status()
        one_page_bars, _, next_page_token = r.json().values()
        one_page_bars = [list(b.values()) for b in one_page_bars]
        bars += one_page_bars
        payload['page_token'] = next_page_token
        if next_page_token is None:
            break
    
    df = pd.DataFrame(data=bars, columns=columns)
    df['timestape'] = df['timestape'].apply(lambda x: pyrfc3339.parse(x))
    return df

def main():

    start = datetime(2021, 7, 15 ,10 ,20 , tzinfo=USATimeZone)
    end = datetime(2021, 7, 15, 10, 25, tzinfo=USATimeZone)
    df = getHistoryBarsData('AAPL', start, end, Resolution.Min)
    print(df)


if __name__ == '__main__':
    main()