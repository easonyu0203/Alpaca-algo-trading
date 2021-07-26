from collections import deque

class RollingWindow:
    '''
    the lastest data is at index 0 and oldest is at index -1
    '''
    def __init__(self, window_size) -> None:
        self._rollingWindow = deque(maxlen=window_size)
        self._window_size = window_size

    def Update(self, data):
        self._rollingWindow.appendleft(data)

    def __getitem__(self, index):
        return self._rollingWindow[index]

    @property
    def is_ready(self):
        return len(self._rollingWindow) == self._window_size


if __name__ == '__main__':
    test = RollingWindow(10)
    for i in range(10):
        test.Update(i)
    print(sum(test))