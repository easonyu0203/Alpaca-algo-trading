from collections import namedtuple
from logging import NOTSET
from .Account import Account
from .Position import Position

PortfolioTarget = namedtuple('PortfolioTarget', ['symbol', 'percentage'])

class Portfolio:
    def __init__(self, account: Account) -> None:
        self.account = account
    
    @property
    def open_positions(self):
        return Position.get_all_open_position()
    
    def have_invested(self, symbol=None):
        '''
        if symbol is None, check whether have invested any money,
        else check have invested in symbol
        '''
        if symbol is None:
            return not (self.open_positions == {})
        else:
            return (Position.get_open_position(symbol) != None)


if __name__ == '__main__':
    account = Account()
    portfolio = Portfolio(account)
    print(portfolio.have_invested)