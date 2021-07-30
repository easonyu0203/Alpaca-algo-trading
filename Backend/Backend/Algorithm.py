from datetime import date, datetime
import pandas as pd
import threading
from logging import log
from dotenv import load_dotenv; load_dotenv()
import os

from .StreamData import StreamData
from .Account import Account
from .Order import Order
from .Portfolio import Portfolio, PortfolioTarget
from .Setting import Setting
from .Position import Position
from .Time import Time
from .Event import EventListener, EventListenerType
from .MarketStatus import MarketStatus
from .Resolution import Resolution
from .HistoryData import getHistoryBarsData
from .config import USATimeZone

log_path = os.environ.get('Log_Path')

class Algorithm:
    def __init__(self, log=False, debug_log=False) -> None:
        self.subscribe_symbol_set = set()
        self.Stream_data = StreamData(debug_log=False)
        self.Account = Account()
        self.Setting = Setting()
        self.Portfolio = Portfolio(self.Account)
        self.Time = Time(self)
        self.MarketStatus = MarketStatus(self)
        self._dataIn_eventListener = EventListener(self.OnData, EventListenerType.Ondata)
        self._dataIn_eventListener.Subcribe(self.Stream_data.dataIn_event)
        self._debug_log = debug_log
        self._log = log
        self._backtesting = False


    
    def Debug(self, _str):
        if self._debug_log == True:
            print(_str)
    
    def Log(self, s):
        if self._log == False: return

        timestamp = self.Time.now.strftime("%Y/%m/%d, %H:%M:%S")
        with open(log_path, 'a') as f:
            out = f'[{timestamp}] {s}\n'
            f.write(out)


    def Initialize(self):
        pass

    def OnData(self, data):
        pass

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
        self.Debug(f'buy {symbol} for {dollar_amount}')
        Order.simple_order(symbol, dollar_amount)
    
    def Liquidate(self, symbol=None):
        '''
        liquidate all equity if symbol=None or only that symbol
        '''
        if symbol is None:
            self.Debug('liquidating all position')
            Position.close_all_position()
        else:
            self.Debug(f'liquidating {symbol}')
            Position.close_position(symbol)

    def SetHolding(self, symbol, percentage):
        '''
        use perentage of your buying power to calculate how much to buy,
        better liquidate first to free up buying power
        '''
        assert 0 <= percentage <= 1

        dollar_amount = self.Account.buying_power * self.Setting.with_cash_buffer * percentage
        self.SimpleOrder(symbol, dollar_amount)

    def History(self, bar_count, resolution, start=None, end=None) -> pd.DataFrame:
        '''
        get history bar data of all symbol for lastest 'bar_count' bars for this resolution
        return dataframe
        two level index ['symbol', 'timestamp']
        colume ['open', 'high', 'low', 'close', 'volume']

        '''
        symbols = self.subscribe_symbol_set
        df_list = []
        thread_list = []

        def runner(df_list, symbol, bar_count, resolution, start, end, algo):
            df = getHistoryBarsData(symbol, bar_count, resolution, start=start, end=end, algo=algo)
            df['symbol'] = symbol
            df_list.append(df)

        for symbol in symbols:
            thread_list.append(threading.Thread(target=runner, args=(df_list, symbol, bar_count, resolution, start, end, self)))
        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()
        out_df = pd.concat(df_list).reset_index().set_index(['symbol', 'timestamp'])
        return out_df


    def _check_for_listening_stream_data(self):
        '''
        check market status and decide whether connect to streaming data or not
        '''
        if self.MarketStatus.CurrentMarketStatus() == self.MarketStatus.Close and self.Stream_data.is_listening == True:
            self.Debug('Ending connection with Alpaca streaming data')
            self.Stream_data.End_listen_stream_data()
        elif self.MarketStatus.CurrentMarketStatus() == self.MarketStatus.OpenSoon and self.Stream_data.is_listening == False:
            self.Debug('Start conection with Alpaca streaming data')
            self.Stream_data.Start_listen_stream_data(self.subscribe_symbol_set)
        elif self.MarketStatus.CurrentMarketStatus() == self.MarketStatus.Open and self.Stream_data.is_listening == False:
            self.Debug('Start conection with Alpaca streaming data')
            self.Stream_data.Start_listen_stream_data(self.subscribe_symbol_set)
        elif self.MarketStatus.CurrentMarketStatus() == self.MarketStatus.CloseSoon and self.Stream_data.is_listening == True:
            self.Debug('Ending connection with Alpaca streaming data')
            self.Stream_data.End_listen_stream_data()
        else:
            pass
            # self.Debug('stay current connection/unconnection')
    

    '''
    Backtesting method
    '''
    def StartDate(self, year: int, month: int, day: int):
        self._start_date = datetime(year, month, day, tzinfo=USATimeZone)
        self.Time.backtest_now = self._start_date
    
    def EndDate(self, year: int, month: int, day: int):
        self._end_date = datetime(year, month, day, tzinfo=USATimeZone)
    
    def _is_end_date(self):
        return self.Time.now >= self._end_date
    
    def SetCash(self, cash):
        self._cash = cash
    
    def _set_backtest(self):
        self._backtesting = True
        
    
    def _get_backtest_history_data_in(self):
        '''
        return dataframe of history data that will stream in to OnData method in backtesting
        '''
        #get start, end date
        start = self._start_date
        end = self._end_date
        if end is None: end = date.today()
        start, end = datetime(start.year, start.month, start.day, tzinfo=USATimeZone), datetime(end.year, end.month, end.day, tzinfo=USATimeZone)
        history = self.History(0, Resolution.Min, start=start, end=end)
        return history
    
    @property
    def _is_backtesting(self):
        return self._backtesting
        





def live_trading():
    my_algo = Algorithm(Debug=True)
    my_algo.Initialize()
    my_algo._check_for_listening_stream_data()

def main():
    my_algo = Algorithm(Debug=True)
    tickers = ['GOOGL', 'TSLA', 'SPY']
    my_algo.Initialize()
    my_algo.Stream_data.Start_listen_stream_data(list(my_algo.subscribe_symbol_set))

if __name__ == '__main__':
    main()