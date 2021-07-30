from datetime import datetime

from .config import USATimeZone
from .Resolution import Resolution
# from .Algorithm import Algorithm


class Time:
    def __init__(self, algo) -> None:
        self._algo = algo
        self.backtest_now = None

    @property
    def now(self) -> datetime:
        if self._algo._is_backtesting == False:
            #live trading
            return datetime.now(USATimeZone)
        else:
            #backtest
            assert self.backtest_now is not None
            return self.backtest_now
    
    def forward(self, resolution: Resolution):
        self.backtest_now += Resolution.timedelta_object(resolution)
