from .RollingWindow import RollingWindow

class Indicator:
    '''
    Interface of Indicator
    '''
    def __init__(self) -> None:
        pass
    
    def Update(self, data):
        pass

    @property
    def is_ready(self):
        pass

    @property
    def value(self):
        assert self.is_ready == True


