from logging import log
from typing import List
import json
import os
from dotenv import load_dotenv; load_dotenv()
import websocket
import ssl

authentication_header = {
    'APCA-API-KEY-ID': os.environ.get('APCA-API-KEY-ID'),
    'APCA-API-SECRET-KEY': os.environ.get('APCA-API-SECRET-KEY')
}

class StreamData:
    def __init__(self, log=False) -> None:
        self.log = log
        self.subcribeCount = 0
        

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
        self.subcribeCount = len(tickers)
        tickers = str(tickers).replace('\'', '\"')
        subscribe_str = f'{{"action":"subscribe","bars":{tickers}}}'
        self.ws.send(subscribe_str)
        subscribe_response = self.ws.recv()
        self.Log(subscribe_response)

    def ListenData(self, OnData):
        while(True):
            print('waiting data...')
            #since alpaca stream one symbol at a time, I concate all data in a time slice to one bar_data
            bar_data = []
            for _ in range(self.subcribeCount):
                b = json.loads(self.ws.recv())
                bar_data += b
            self.Log(bar_data)
            bar_data = self._process_alpaca_steam_data(bar_data)
            #call back function
            OnData(bar_data)
    
    def _process_alpaca_steam_data(self, bar_data):
        out_dict = dict()
        for b in bar_data:
            b['symbol'] = b.pop('S')
            b['open'] = b.pop('o')
            b['high'] = b.pop('h')
            b['low'] = b.pop('l')
            b['close'] = b.pop('c')
            b['volume'] = b.pop('v')
            b['timestamp'] = b.pop('t')
            out_dict[b['symbol']] = b
        return out_dict
    

def main():

    tickers = ['GOOGL', 'TSLA', 'SPY']
    # SubscribeMinBarsData(tickers)
    stream_data = StreamData(log=True)
    stream_data.ConnectStreaming()
    stream_data.SubcribeSymbols(tickers)
    stream_data.ListenData(lambda x: x)

if __name__ == '__main__':
    main()