from logging import log
from typing import List
import requests
import json
from datetime import datetime
import os
import pandas as pd
import pyrfc3339
from dotenv import load_dotenv; load_dotenv()
from config import USATimeZone
import websocket
import ssl

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

class StreamData:
    def __init__(self, log=False) -> None:
        self.log = log
        

    def SetLog(self, log: bool):
        self.log = log
    
    def Log(self, _str: str):
        if self.log == True:
            print(_str)

    def ConnectStreaming(self):
        source = 'iex'
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.ws.connect(f"wss://stream.data.alpaca.markets/v2/{source}")
        connect_response = self.ws.recv()
        self.Log(connect_response)
        #Establishment: authenticate
        auth = f'{{"action": "auth", "key": "{os.environ.get("APCA-API-KEY-ID")}", "secret": "{os.environ.get("APCA-API-SECRET-KEY")}"}}'
        self.ws.send(auth)
        auth_response = self.ws.recv()
        self.Log(auth_response)
    
    def SubcribeSymbols(self, tickers:List):
        tickers = str(tickers).replace('\'', '\"')
        subscribe_str = f'{{"action":"subscribe","bars":{tickers}}}'
        self.ws.send(subscribe_str)
        subscribe_response = self.ws.recv()
        self.Log(subscribe_response)

    def ListenData(self, OnData):
        while(True):
            bar_data = self.ws.recv()
            self.Log(bar_data)
            #call back function
            OnData(bar_data)
    

def main():

    # start = datetime(2021, 7, 15 ,10 ,20 , tzinfo=USATimeZone)
    # end = datetime(2021, 7, 15, 10, 25, tzinfo=USATimeZone)
    # df = getHistoryBarsData('AAPL', start, end, Resolution.Min)
    # print(df)

    tickers = ['GOOGL', 'TSLA', 'SPY']
    # SubscribeMinBarsData(tickers)
    stream_data = StreamData(log=True)
    stream_data.ConnectStreaming()
    stream_data.SubcribeSymbols(tickers)
    stream_data.ListenData(lambda x: x)

if __name__ == '__main__':
    main()