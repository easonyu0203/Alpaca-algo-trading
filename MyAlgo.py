from Backend.Algorithm import Algorithm


class MyAlogo(Algorithm):
    def Initialize(self):
        print('myalgo init...')
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