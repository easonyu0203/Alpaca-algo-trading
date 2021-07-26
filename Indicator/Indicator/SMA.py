from Backend.Indicator import Indicator
from Backend.RollingWindow import RollingWindow


class SMA(Indicator):

    def __init__(self, window_size) -> None:
        self._window_size = window_size
        self._rollingWindow = RollingWindow(window_size=window_size)


    def Update(self, data):
        self._rollingWindow.Update(data)

    @property    
    def is_ready(self):
        return self._rollingWindow.is_ready

    @property
    def value(self):
        super().value
        _value = sum(self._rollingWindow) / self._window_size
        return _value
    

if __name__ == '__main__':
    sma = SMA(10)
    for i in range(10):
        sma.Update(i)
    print(sma.value)