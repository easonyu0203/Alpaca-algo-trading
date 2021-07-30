import pandas as pd

from Backend.Algorithm import Algorithm
from Backend.Resolution import Resolution
from Backend.RollingWindow import RollingWindow
from Indicator.SMA import SMA


class MyAlogo(Algorithm):
    def Initialize(self):
        self.Log('myalgo init...')
        #backtest
        self.StartDate(2021, 7, 29)
        self.EndDate(2021, 7, 30)
        self.SetCash(1_000_000)

        self.sma03_dic = {}
        self.sma10_dic = {}
        self.sma03_rolling_dic = {}
        self.sma10_rolling_dic = {}
        self.low_rolling_dic ={}
        self.high_rolling_dic ={}
        self.symbols = [
            'SPY',
            'TSLA',
            'AAPL',
            'GOOGL',
            'AMD',
            'GE',
            'MSFT',
            'CCL',
            'FB',
            'NVDA',
            'BA',
            'BAC',
            'INTC',
        ]
        self.current_hold_symbol = None
        for symbol in self.symbols:
            self.AddEquity(symbol)
        df = self.History(30, Resolution.Min)
        for symbol in self.symbols:
            self.EachInit(symbol, df.loc[symbol])
        
        #liquidate all first
        self.Liquidate()

    def OnData(self, data):
        self.Log('=========Ondata========')
        for symbol in self.symbols:
            self.EachUpdateIndicator(symbol, data)
        
        if self.Portfolio.have_invested() == False:
            for symbol in self.symbols:
                buy_this = self.EachCheckBuy(symbol, data) 
                if buy_this:
                    self.current_hold_symbol = symbol
                    break
        else:
            self.EachCheckSell(self.current_hold_symbol, data)
        

        self.Log('=========================\n')

    def EachInit(self, symbol, df):
        self.Log(f'init {symbol}')
        self.sma03_dic[symbol] = SMA(self, symbol, 3)
        self.sma10_dic[symbol] = SMA(self, symbol, 10)
        self.sma10_rolling_dic[symbol] = RollingWindow(13)
        self.sma03_rolling_dic[symbol] = RollingWindow(2)
        self.low_rolling_dic[symbol] = RollingWindow(2)
        self.high_rolling_dic[symbol] = RollingWindow(2)

        for bar in df.itertuples():
            self.sma03_dic[symbol].Update(bar.close)
            self.sma10_dic[symbol].Update(bar.close)
            self.low_rolling_dic[symbol].Update(bar.low)
            self.high_rolling_dic[symbol].Update(bar.high)
            if self.sma03_dic[symbol].is_ready:
                self.sma03_rolling_dic[symbol].Update(self.sma03_dic[symbol].value)
            if self.sma10_dic[symbol].is_ready:
                self.sma10_rolling_dic[symbol].Update(self.sma10_dic[symbol].value)
    
    def EachUpdateIndicator(self, symbol, data):
        #manual update indicator
        if self.sma10_dic[symbol].is_ready:
            self.sma10_rolling_dic[symbol].Update(self.sma10_dic[symbol].value)
        if self.sma03_dic[symbol].is_ready:
            self.sma03_rolling_dic[symbol].Update(self.sma03_dic[symbol].value)
        self.low_rolling_dic[symbol].Update(data[symbol].low)
        self.high_rolling_dic[symbol].Update(data[symbol].high)
        if self.sma10_rolling_dic[symbol].is_ready == False:
            self.Log('indicator not ready yet..')
            return
        
        self.Debug(f'{symbol} sma03: {self.sma03_dic[symbol].value:.2f} sma10: {self.sma10_dic[symbol].value:.2f} low: {data[symbol].low:.2f} high: {data[symbol].high:.2f}')
    

    def EachCheckBuy(self, symbol, data) -> bool:
        '''
        return True if buy
        '''
        #if Market not open yet, don't place any order
        if self.MarketStatus.CurrentMarketStatus() != self.MarketStatus.Open:
            self.Debug('===Market not open, dont place order===')
            return

        #find buy point when not invested
        if self.have_down_trend(symbol) == True:
            if self.cross_up(symbol) == True:
                self.Debug(f'===BUY {symbol}===')
                self.SetHolding(symbol, 1)
                return True
        else:
            return False
    
    def EachCheckSell(self, symbol, data):
        if self.cross_down(symbol):
            self.Debug(f'===SELL {symbol}===')
            self.Liquidate(symbol)

    
    def have_down_trend(self, symbol):
        assert self.sma10_rolling_dic[symbol].is_ready == True
        #if 80% of previous sma 10 are going down, then have down trend
        #the two lastest point dont use 
        indi_list = list(self.sma10_rolling_dic[symbol])[2:]
        cnt = 0
        for pre, now in zip(indi_list[1:], indi_list[:-1]):
            if pre >= now: 
                cnt += 1
        self.Debug(f'{symbol} down pc: {cnt}/{len(indi_list) - 1}')
        if cnt / (len(indi_list) - 1)>= 0.8:
            return True
        else:
            return False
    
    def cross_down(self, symbol):
        assert self.sma03_rolling_dic[symbol].is_ready == True
        assert self.low_rolling_dic[symbol].is_ready == True
        assert self.high_rolling_dic[symbol].is_ready == True
        assert self.sma10_rolling_dic[symbol].is_ready == True
        if self.low_rolling_dic[symbol][1] > self.sma10_rolling_dic[symbol][1] and self.low_rolling_dic[symbol][0] < self.sma10_rolling_dic[symbol][0]:
            return True
        else:
            return False
    
    def cross_up(self, symbol):
        assert self.sma03_rolling_dic[symbol].is_ready == True
        assert self.low_rolling_dic[symbol].is_ready == True
        assert self.high_rolling_dic[symbol].is_ready == True
        assert self.sma10_rolling_dic[symbol].is_ready == True
        if self.high_rolling_dic[symbol][1] < self.sma10_rolling_dic[symbol][1] and self.high_rolling_dic[symbol][0] > self.sma10_rolling_dic[symbol][0]:
            return True
        else:
            return False