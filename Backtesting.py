from Backend.Resolution import Resolution
from dotenv import load_dotenv; load_dotenv()
from datetime import date, datetime, timezone
import pandas as pd
from time import sleep, time

from TestAlgo import TestAlgo
from Backend.config import USATimeZone
from Backend.HistoryData import getHistoryBarsData

def Backtesting():
    algo = TestAlgo(log=True, debug_log=True)
    algo._set_backtest()
    algo.Initialize()

    #OnData history data
    history = algo._get_backtest_history_data_in().reset_index().set_index('timestamp')
    print(history)

    cnt = 0
    s = time()
    while(not algo._is_end_date()):
        current = algo.Time.now
        #OnData
        try:
            _index_day = pd.Timestamp(current.astimezone(timezone.utc))
            current_on_data = history.loc[_index_day]
            # print(current)
            cnt += 1
        except KeyError:
            pass

        algo.Time.forward(Resolution.Min)
    
    e = time()
    print(f'take: {e-s}')
    print(cnt)
        

    



if __name__ == '__main__':
    Backtesting()