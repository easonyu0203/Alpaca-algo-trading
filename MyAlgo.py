from Backend.Algorithm import Algorithm
from Backend.HistoryData import getHistoryBarsData
from Backend.MarketStatus import MarketStatus
from Indicator.SMA import SMA
from Backend.Resolution import Resolution
from Backend.RollingWindow import RollingWindow


class MyAlogo(Algorithm):
    def Initialize(self):
        self.Log('myalgo init...')
        #testing
        self.AddEquity('TSLA')
        self.sma03 = SMA(self, 'TSLA', 3)
        self.sma10 = SMA(self, 'TSLA', 10)
        self.sma50 = SMA(self, 'TSLA', 50)
        self.sma10_rolling = RollingWindow(13)
        self.sma03_rolling = RollingWindow(2)
        
        #warm up sma
        self.Log('Warm Up')
        for bar in getHistoryBarsData('TSLA', 50, Resolution.Min).itertuples():
            self.sma03.Update(bar.close)
            self.sma10.Update(bar.close)
            self.sma50.Update(bar.close)
            if self.sma03.is_ready:
                self.sma03_rolling.Update(self.sma03.value)
            if self.sma10.is_ready:
                self.sma10_rolling.Update(self.sma10.is_ready)

    def OnData(self, data):
        self.Log('=========Ondata========')
        #manual update indicator
        if self.sma10.is_ready:
            self.sma10_rolling.Update(self.sma10.value)
        if self.sma03.is_ready:
            self.sma03_rolling.Update(self.sma03.value)
        if self.sma50.is_ready == False:
            self.Log('indicator not ready yet..')
            return

        self.Log(f'sma 03: {self.sma03.value}')
        self.Log(f'sma 10: {self.sma10.value}')
        self.Log(f'sma 50: {self.sma50.value}')
        current_price = data['TSLA'].close
        self.Log(f'price: {current_price}')
        if self.have_down_trend: self.Log('have down trend')
        else: self.Log('dont have down trend')
        if self.sma03.value > self.sma50.value: self.Log('price above sma 50')
        if self.cross_down: self.Log('cross down')
        elif self.cross_up: self.Log('cross up')
        else: self.Log('no corss')
        
        #if Market not open yet, don't place any order
        if MarketStatus.CurrentMarketStatus() != MarketStatus.Open:
            self.Log('===Market not open, dont place order===')
            return

        #find buy point when not invested
        if self.Portfolio.have_invested == False:
                if self.have_down_trend == True:
                    if self.cross_up == True:
                        self.Log('===BUY===')
                        self.SetHolding('TSLA', 1)
        else:
            if self.cross_down == True:
                self.Log('===SELL===')
                self.Liquidate('TSLA')
        self.Log('=========================\n')


    
    @property
    def have_down_trend(self):
        assert self.sma10_rolling.is_ready == True
        #if 80% of previous sma 10 are going down, then have down trend
        #the two lastest point dont use 
        indi_list = list(self.sma10_rolling)[2:]
        cnt = 0
        for pre, now in zip(indi_list[1:], indi_list[:-1]):
            if pre >= now: 
                cnt += 1
        self.Log(f'down pc: {cnt}/{len(indi_list) - 1}')
        if cnt / (len(indi_list) - 1)>= 0.66:
            return True
        else:
            return False
    
    @property
    def cross_down(self):
        assert self.sma03_rolling.is_ready == True
        assert self.sma10_rolling.is_ready == True
        if self.sma03_rolling[1] > self.sma10_rolling[1] and self.sma03_rolling[0] < self.sma10_rolling[0]:
            return True
        else:
            return False
    
    @property
    def cross_up(self):
        assert self.sma03_rolling.is_ready == True
        assert self.sma10_rolling.is_ready == True
        if self.sma03_rolling[1] < self.sma10_rolling[1] and self.sma03_rolling[0] > self.sma10_rolling[0]:
            return True
        else:
            return False