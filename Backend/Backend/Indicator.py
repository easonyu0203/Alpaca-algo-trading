from .Event import EventListener, EventListenerType
from .Algorithm import Algorithm

class Indicator:
    '''
    Interface of Indicator
    Indicator will auto update when data in
    '''

    def __init__(self, algo: Algorithm) -> None:
        self.dataIn_eventListener = EventListener(self.Ondata, EventListenerType.Indicator)
        self.dataIn_eventListener.Subcribe(algo.Stream_data.dataIn_event)

    def Ondata(self, data):
        print('[indicator] dont have Ondata method')
    
    def Update(self, new_data_point):
        print('[indicator] dont have update method')

    @property
    def is_ready(self):
        print('[indicator] dont have is_ready attribute')
        

    @property
    def value(self):
        assert self.is_ready == True


