import threading

from .StreamData import StreamData
from .Account import Account
from .Order import Order
from .Portfolio import Portfolio, PortfolioTarget
from .Setting import Setting
from .Position import Position
from .Event import EventListener
from .MarketStatus import MarketStatus

class Algorithm:
    def __init__(self, log=False) -> None:
        self.subscribe_symbol_set = set()
        self.Stream_data = StreamData(log=True)
        self.Account = Account()
        self.Setting = Setting()
        self.Portfolio = Portfolio(self.Account)
        self.dataIn_eventListener = EventListener(self.OnData)
        self.dataIn_eventListener.Subcribe(self.Stream_data.dataIn_event)
        self._log = log
    
    def Log(self, _str):
        if self._log == True:
            print(_str)

    def Initialize(self):
        #testing
        self.AddEquity('SPY')
        self.AddEquity('TSLA')

    def OnData(self, data):
        print('Ondata..')
        if not self.Portfolio.have_invested:
            print('no portfolio')
            self.SetHolding('TSLA', 1)
        else:
            self.Liquidate('TSLA')

    def AddEquity(self, symbol):
        '''
        Add this equity to my universe
        '''
        self.subscribe_symbol_set.add(symbol)

    def SimpleOrder(self, symbol, dollar_amount):
        '''
        place a market day order for 'ticker' for 'dollar_amount'
        I assume there will not be any reject or cancle for a order, since this is a market day order, it is unlikely being reject
        '''
        self.Log(f'buy {symbol} for {dollar_amount}')
        Order.simple_order(symbol, dollar_amount)
    
    def Liquidate(self, symbol=None):
        '''
        liquidate all equity if symbol=None or only that symbol
        '''
        if symbol is None:
            self.Log('liquidating all position')
            Position.close_all_position()
        else:
            self.Log(f'liquidating {symbol}')
            Position.close_position(symbol)

    def SetHolding(self, symbol, percentage):
        '''
        use perentage of your buying power to calculate how much to buy,
        better liquidate first to free up buying power
        '''
        assert 0 <= percentage <= 1

        dollar_amount = self.Account.buying_power * self.Setting.with_cash_buffer * percentage
        self.SimpleOrder(symbol, dollar_amount)

    def _check_for_listening_stream_data(self):
        '''
        check market status and decide whether connect to streaming data or not
        '''
        if MarketStatus.CurrentMarketStatus() == MarketStatus.Close and self.Stream_data.is_listening == True:
            self.Log('Ending connection with Alpaca streaming data')
            self.Stream_data.End_listen_stream_data()
        elif MarketStatus.CurrentMarketStatus() == MarketStatus.OpenSoon and self.Stream_data.is_listening == False:
            self.Log('Start conection with Alpaca streaming data')
            self.Stream_data.Start_listen_stream_data(self.subscribe_symbol_set)
        elif MarketStatus.CurrentMarketStatus() == MarketStatus.Open and self.Stream_data.is_listening == False:
            self.Log('Start conection with Alpaca streaming data')
            self.Stream_data.Start_listen_stream_data(self.subscribe_symbol_set)
        elif MarketStatus.CurrentMarketStatus() == MarketStatus.CloseSoon and self.Stream_data.is_listening == True:
            self.Log('Ending connection with Alpaca streaming data')
            self.Stream_data.End_listen_stream_data()
        else:
            self.Log('stay current connection/unconnection')





def live_trading():
    my_algo = Algorithm(log=True)
    my_algo.Initialize()
    my_algo._startLive()

def main():
    live_trading()

if __name__ == '__main__':
    main()