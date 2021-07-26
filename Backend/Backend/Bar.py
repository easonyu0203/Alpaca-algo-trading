import pyrfc3339

class Bar:
    def __init__(self, info_dict: dict) -> None:
        '''
        dictionary need to have
        [symbol, open, high, low, close, volume, timestamp(in RFC-3339 format)]
        '''
        self.info_dict = info_dict
        self.symbol = str(info_dict['symbol'])
        self.open = float(info_dict['open'])
        self.high = float(info_dict['high'])
        self.low = float(info_dict['low'])
        self.close = float(info_dict['close'])
        self.volume = int(info_dict['volume'])
        self.timestamp = pyrfc3339.parse(info_dict['timestamp'])

    def __repr__(self) -> str:
        return str(self.info_dict)