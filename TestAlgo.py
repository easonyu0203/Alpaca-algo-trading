from Backend.Position import Position
import pandas as pd

from Backend.Algorithm import Algorithm
from Backend.Resolution import Resolution
from Backend.RollingWindow import RollingWindow
from Indicator.SMA import SMA


class TestAlgo(Algorithm):
    def Initialize(self):

        self.StartDate(2021,7,29)
        self.EndDate(2021,7,30)
        self.SetCash(100_000)

        self.AddEquity('TSLA')
        self.AddEquity('SPY')
        self.sma_t = SMA(self, 'TSLA', 10)
        self.sma_s = SMA(self, 'SPY', 10)

        df = self.History(10, Resolution.Min)
        for bar in df.loc['TSLA'].itertuples():
            self.sma_t.Update(bar.close)
        for bar in df.loc['SPY'].itertuples():
            self.sma_s.Update(bar.close)
    
    def OnData(self, data):
        if self.MarketStatus.CurrentMarketStatus() != self.MarketStatus.Open:
            return

        if self.Portfolio.have_invested == False:
            self.Log('===BUY===')
            # self.SetHolding('TSLA', 1)