from datetime import timedelta

class Resolution:
    Min = '1Min'
    Hour = '1Hour'
    Day = '1Day'

    def timedelta_object(resolution):
        if resolution == Resolution.Min:
            return timedelta(minutes=1)
        elif resolution == Resolution.Hour:
            return timedelta(hours=1)
        elif resolution == Resolution.Day:
            return timedelta(days=1) 