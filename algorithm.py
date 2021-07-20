from typing import List
from getData import StreamData
from account import Account
from order import simple_order
from collections import namedtuple

PortfolioTarget = namedtuple('PortfolioTarget', ['symbol', 'percentage'])

class Algorithm:
    def __init__(self) -> None:
        self.subscribe_symbol_set = set()
        self.stream_data = StreamData(log=True)
        self.account = Account

    def Initialize(self):
        #testing
        self.AddEquity('SPY')

    def OnData(self, data):
        pass

    def _startLive(self):
        self.stream_data.ConnectStreaming()
        self.stream_data.SubcribeSymbols(list(self.subscribe_symbol_set))
        self.stream_data.ListenData(OnData=self.OnData)

    def AddEquity(self, symbol):
        '''
        Add this equity to my universe
        '''
        self.subscribe_symbol_set.add(symbol)

    def SimpleOrder(symbol, dollar_amount):
        '''
        place a market day order for 'ticker' for 'dollar_amount'
        I assume there will not be any reject or cancle for a order, since this is a market day order, it is unlikely being reject
        '''
        simple_order(symbol, dollar_amount)
    
    def Liquidate(self, symbol=None):
        '''
        liquidate all equity if symbol=None or only that symbol
        '''
        pass

    def SetHolding(self, porfolioTargets:List[PortfolioTarget]):
        '''
        use perentage of your buying power to calculate how much to buy,
        better liquidate first to free up buying power
        '''
        pass




def live_trading():
    my_algo = Algorithm()
    my_algo.Initialize()

def main():
    pass

if __name__ == '__main__':
    main()