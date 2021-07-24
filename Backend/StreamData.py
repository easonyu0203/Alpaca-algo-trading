from enum import Flag
from dotenv import load_dotenv; load_dotenv()
from typing import List
import json
import os
import websocket
import ssl
from queue import SimpleQueue
import threading

from .Event import Event, EventListener, EventType

authentication_header = {
    'APCA-API-KEY-ID': os.environ.get('APCA-API-KEY-ID'),
    'APCA-API-SECRET-KEY': os.environ.get('APCA-API-SECRET-KEY')
}

class StreamData:
    def __init__(self, log=False) -> None:
        self.log = log
        self.subcribeCount = 0
        self._buffer = SimpleQueue()
        self.dataIn_event = Event(EventType.DataIn)
        self.is_listening = False
        self.listen_data_thread = None

    def Update(self):
        if not self._buffer.empty() and self.is_listening == True:
            data = self._buffer.get()
            self.dataIn_event.Emit(data)
        

    def SetLog(self, log: bool):
        self.log = log
    
    def Log(self, _str: str):
        if self.log == True:
            print(_str)

    def Start_listen_stream_data(self, subscribe_symbol_set):
        '''
        start listening streaming data from another thread
        '''
        self._clear_buffer()
        self.is_listening = True

        if self.listen_data_thread is None or self.listen_data_thread.is_alive() == False:
            self.ConnectStreaming()
            self.SubcribeSymbols(list(subscribe_symbol_set))
            self.listen_data_thread = threading.Thread(target=self.ListenData)
            self.listen_data_thread.start()
    
    def End_listen_stream_data(self):
        self.is_listening = False

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

    def ListenData(self):
        while(self.is_listening):
            #since alpaca stream one symbol at a time, I concate all data in a time slice to one bar_data
            bar_data = []
            for _ in range(self.subcribeCount):
                b = json.loads(self.ws.recv())
                bar_data += b
            self.Log(bar_data)
            bar_data = self._process_alpaca_steam_data(bar_data)
            self._buffer.put(bar_data)
            
        self._clear_buffer()
    

    def _clear_buffer(self):
        #clear buffer
        while self._buffer.empty() is not True:
            self._buffer.get()

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