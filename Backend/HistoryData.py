from time import time
from dotenv import load_dotenv; load_dotenv()
from logging import log
from typing import List
import requests
import os
import pandas as pd
import pyrfc3339
from datetime import datetime, timedelta

from .config import USATimeZone
from .MarketStatus import MarketStatus

authentication_header = {
    'APCA-API-KEY-ID': os.environ.get('APCA-API-KEY-ID'),
    'APCA-API-SECRET-KEY': os.environ.get('APCA-API-SECRET-KEY')
}

class Resolution:
    Min = '1Min'
    Hour = '1Hour'
    Day = '1Day'

    def timedelta_object(resolution):
        if resolution == Resolution.Min:
            return timedelta(minutes=1)
        elif resolution == Resolution.Hour:
            return timedelta(hours=1)
        elif resolution == Resolution.Day:
            return timedelta(days=1) 

    
def getHistoryBarsData(symbol, bar_count, resolution):
    '''
    get history bar data of symbol for lastest 'bar_count' bars for this resolution
    '''
    start, end = _get_start_end_time(bar_count, resolution)
    columns = ['timestape', 'open', 'high', 'low', 'close', 'volume']
    base_url = os.environ.get('APCA_API_DATA_URL')
    trade_url =  f'{base_url}/v2/stocks/{symbol}/bars'
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
    return df.iloc[-bar_count:]

def _get_start_end_time(bar_count, resolution):
    now = datetime.now(USATimeZone)# - timedelta(days=1)
    end = now
    if resolution == Resolution.Min:
        end = datetime(end.year, end.month, end.day, end.hour, end.minute, tzinfo=USATimeZone) - timedelta(minutes=1)
    elif resolution == Resolution.Hour:
        end = datetime(end.year, end.month, end.day, end.hour, tzinfo=USATimeZone) - timedelta(hours=1)
    elif resolution == Resolution.Day:
        end = datetime(end.year, end.month, end.day, tzinfo=USATimeZone) - timedelta(days=1)
    
    start = end - Resolution.timedelta_object(resolution) * bar_count
    if resolution == Resolution.Day:
        start = end - Resolution.timedelta_object(resolution) * bar_count * 2

    
    return start, end


def main():

    df = getHistoryBarsData('AAPL', 100, Resolution.Min)
    print(df)



if __name__ == '__main__':
    # print(pyrfc3339.generate(datetime.now(USATimeZone)))
    main()