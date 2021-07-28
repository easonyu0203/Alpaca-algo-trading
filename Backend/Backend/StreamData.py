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
from .Bar import Bar

authentication_header = {
    'APCA-API-KEY-ID': os.environ.get('APCA-API-KEY-ID'),
    'APCA-API-SECRET-KEY': os.environ.get('APCA-API-SECRET-KEY')
}

class StreamData:
    '''
    for event listener, the data is a dictionary key by 'symbol', value is a Bar object
    '''
    def __init__(self, debug_log=False) -> None:
        self._source = 'sip'
        self._debug_log = debug_log
        self.subcribeCount = 0
        self._buffer = SimpleQueue()
        self.dataIn_event = Event(EventType.DataIn)
        self.is_listening = False
        self.listen_data_thread = None
        self.last_data_timestamp = None

    def Check_DataIn_Event(self):
        if not self._buffer.empty() and self.is_listening == True:
            data = self._buffer.get()
            self.dataIn_event.Emit(data)
        
    
    def Debug(self, _str: str):
        if self._debug_log == True:
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
        source = self._source
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.ws.connect(f"wss://stream.data.alpaca.markets/v2/{source}")
        connect_response = self.ws.recv()
        self.Debug(connect_response)
        #Establishment: authenticate
        auth = f'{{"action": "auth", "key": "{os.environ.get("APCA-API-KEY-ID")}", "secret": "{os.environ.get("APCA-API-SECRET-KEY")}"}}'
        self.ws.send(auth)
        auth_response = self.ws.recv()
        self.Debug(auth_response)
    
    def SubcribeSymbols(self, tickers:List):
        self.subcribeCount = len(tickers)
        tickers = str(tickers).replace('\'', '\"')
        subscribe_str = f'{{"action":"subscribe","bars":{tickers}}}'
        self.ws.send(subscribe_str)
        subscribe_response = self.ws.recv()
        self.Debug(subscribe_response)

    def ListenData(self):
        while(self.is_listening):
            #since alpaca stream one symbol at a time, I concate all data in a time slice to one bar_data
            bar_data = []
            for _ in range(self.subcribeCount):
                b = json.loads(self.ws.recv())
                bar_data += b
            self.Debug(f'[data in]{bar_data}')
            bar_data = self._process_alpaca_steam_data(bar_data)
            current_timestamp = list(bar_data.values())[0]['timestamp']
            if self.last_data_timestamp is not None and self.last_data_timestamp == current_timestamp:
                self.Debug('data repeat (alpaca stream problem)')
            else:
                self._buffer.put(bar_data)
                self.last_data_timestamp == current_timestamp
            
        self._clear_buffer()
    

    def _clear_buffer(self):
        #clear buffer
        while self._buffer.empty() is not True:
            self._buffer.get()

    def _process_alpaca_steam_data(self, bar_data) -> dict:
        out_dict = dict()
        for b in bar_data:
            b['symbol'] = b.pop('S')
            b['open'] = b.pop('o')
            b['high'] = b.pop('h')
            b['low'] = b.pop('l')
            b['close'] = b.pop('c')
            b['volume'] = b.pop('v')
            b['timestamp'] = b.pop('t')
            b = Bar(b)
            out_dict[b.symbol] = b
        return out_dict
    

def main():

    tickers = ['GOOGL', 'TSLA', 'SPY']
    # SubscribeMinBarsData(tickers)
    stream_data = StreamData(log=True)
    stream_data.Start_listen_stream_data(tickers)

if __name__ == '__main__':
    main()