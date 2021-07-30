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
from .Resolution import Resolution

authentication_header = {
    'APCA-API-KEY-ID': os.environ.get('APCA-API-KEY-ID'),
    'APCA-API-SECRET-KEY': os.environ.get('APCA-API-SECRET-KEY')
}


    
def getHistoryBarsData(symbol, bar_count, resolution, start=None, end=None, algo=None):
    '''
    get history bar data of symbol for lastest 'bar_count' bars for this resolution
    return dataframe with index by timestamp and colume of ['open', 'high', 'low', 'close', 'volume']
    '''
    if start is None or end is None:
        start, end = _get_start_end_time(bar_count, resolution, algo=algo)
    print('[History data]')
    print(f'start: {start}')
    print(f'end: {end}')
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
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
        one_page_bars = [list(b.values())[:len(columns)] for b in one_page_bars]
        bars += one_page_bars
        payload['page_token'] = next_page_token
        if next_page_token is None:
            break
    df = pd.DataFrame(data=bars, columns=columns)
    df['timestamp'] = df['timestamp'].apply(lambda x: pyrfc3339.parse(x))
    df.set_index('timestamp', inplace=True)
    assert df.shape[0] >= bar_count
    return df.iloc[-bar_count:]

def _get_start_end_time(bar_count, resolution, algo=None):
    now = datetime.now(USATimeZone)# - timedelta(days=1)
    if algo is not None:
        now = algo.Time.now
    end = now
    if resolution == Resolution.Min:
        end = datetime(end.year, end.month, end.day, end.hour, end.minute + 1, tzinfo=USATimeZone)# - timedelta(minutes=20)
    elif resolution == Resolution.Hour:
        end = datetime(end.year, end.month, end.day, end.hour + 1, tzinfo=USATimeZone)# - timedelta(hours=1)
    elif resolution == Resolution.Day:
        end = datetime(end.year, end.month, end.day + 1, tzinfo=USATimeZone)# - timedelta(days=1)

    
    if algo == None: market_state = MarketStatus
    else: market_state = algo.MarketStatus
    if resolution == Resolution.Min or resolution == Resolution.Hour:
        while market_state.CurrentMarketStatus(end) == market_state.Close or market_state.CurrentMarketStatus(end) == market_state.OpenSoon:
            end -= Resolution.timedelta_object(resolution)
        start = end
        have_bar_count = 0 - 10
        while have_bar_count < bar_count:
            start -= Resolution.timedelta_object(resolution)
            if market_state.CurrentMarketStatus(start) == market_state.Open or market_state.CurrentMarketStatus(start) == market_state.CloseSoon:
                have_bar_count += 1
    elif resolution == Resolution.Day:
        start = end - Resolution.timedelta_object(resolution) * bar_count * 2
    else:
        print('resolution dont exit')
        exit()

    return start, end


def main():

    df = getHistoryBarsData('AAPL', 100, Resolution.Min)
    print(df)



if __name__ == '__main__':
    # print(pyrfc3339.generate(datetime.now(USATimeZone)))
    main()