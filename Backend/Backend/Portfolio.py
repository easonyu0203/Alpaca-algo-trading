from collections import namedtuple
from .Account import Account
from .Position import Position

PortfolioTarget = namedtuple('PortfolioTarget', ['symbol', 'percentage'])

class Portfolio:
    def __init__(self, account: Account) -> None:
        self.account = account
    
    @property
    def open_positions(self):
        return Position.get_all_open_position()
    
    @property
    def have_invested(self):
        return not (self.open_positions == {})


if __name__ == '__main__':
    account = Account()
    portfolio = Portfolio(account)
    print(portfolio.have_invested)