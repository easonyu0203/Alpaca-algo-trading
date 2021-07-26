from enum import Enum, auto
import pandas as pd
from datetime import datetime, timedelta

from .config import USATimeZone

class MarketStatus:
    OpenSoon =  0
    Open = 1
    CloseSoon = 2
    Close = 3
    # time interval which consider will open/close soon
    pre_open_interval = timedelta(minutes=10)
    pre_close_interval = timedelta(minutes=10)

    _calendar_df = None

    def get_calendar_df():
        df = pd.read_csv('Data/MarketCalendar',parse_dates=[ [0,1], [0,2]])
        df['date'] = df['date_open'].apply(lambda t: datetime(t.year, t.month, t.day))
        df.set_index('date', inplace=True)
        df.rename(columns={'date_open': 'open', 'date_close': 'close'}, inplace=True)
        return df

    def calendar_df():
        if MarketStatus._calendar_df is None:
            MarketStatus._calendar_df = MarketStatus.get_calendar_df()
        return MarketStatus._calendar_df

    def CurrentMarketStatus(now=None):
        '''
        tell you the market status of now, if 'now' is None than it will use datetime.now(USATimeZone)
        '''
        if now is None:
            now = datetime.now(USATimeZone)
        try:
            open_close_time = MarketStatus.calendar_df().loc[datetime(now.year, now.month, now.day)]
            # print(open_close_time)
            return MarketStatus._status_time_interval(now, open_close_time)
        except KeyError:
            #this day market doesn't open
            return MarketStatus.Close
    
    def _status_time_interval(now, open_close_time):
        now = datetime(now.year, now.month, now.day, now.hour, now.minute)
        # print(f'now: {now}')
        if now < open_close_time['open'] - MarketStatus.pre_open_interval:
            return MarketStatus.Close
        elif open_close_time['open'] - MarketStatus.pre_open_interval <= now < open_close_time['open']:
            return MarketStatus.OpenSoon
        elif open_close_time['open'] <= now < open_close_time['close'] - MarketStatus.pre_close_interval:
            return MarketStatus.Open
        elif open_close_time['close'] - MarketStatus.pre_close_interval <= now < open_close_time['close']:
            return MarketStatus.CloseSoon
        elif open_close_time['close'] <= now:
            return MarketStatus.Close
    


if __name__ == '__main__':
    print(MarketStatus.CurrentMarketStatus())