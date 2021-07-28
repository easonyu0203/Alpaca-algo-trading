from enum import Enum, auto

class EventType:
    '''
    lower number have higher priority
    '''
    DataIn = 10
    Schedule = 0

class EventListenerType:
    Ondata = 10
    Indicator = 0

class Event:
    '''
    A Event object will emit an event and let all EventListner object know and run function respectively
    '''

    _all_event_list = []
    _regist_emit_event = []

    def __init__(self, event_type) -> None:
        self.listener_list = []
        self.type = event_type
        self.payload = None
        Event._all_event_list.append(self)
    
    def _event_loop():
        if Event._regist_emit_event == []:
            return
        Event._regist_emit_event.sort(key=lambda x: x.type)

        for e in Event._regist_emit_event:
            e._actual_emit()
        
        Event._regist_emit_event.clear()

    
    def _register_emit(self, payload):
        self.payload = payload
        Event._regist_emit_event.append(self)

    def _actual_emit(self):
        sorted(self.listener_list, key=lambda x: x._event_listener_type)
        for listener in self.listener_list:
            listener.Callback(self.payload)

    def Emit(self, payload):
        '''
        This will not emit immediately
        '''
        self._register_emit(payload)
        

    def Add_event_listener(self, eventListener):
        self.listener_list.append(eventListener)

    def Remove_event_listener(self, eventListener):
        '''
        if event listener doesn't exit than throw error
        '''
        self.listener_list.remove(eventListener)

class EventListener:
    '''
    Subcribe to an event and a call back function to deal with the event
    '''

    def __init__(self, callback, event_listener_type) -> None:
        self._event_listener_type = event_listener_type
        self._subcribed_event = None
        self.Callback = callback

    def Subcribe(self, event: Event):
        event.Add_event_listener(self)
        self._subcribed_event = event

    def Unsubcribe(self):
        self._subcribed_event.Remove_event_listener(self)


if __name__ == '__main__':
    
    class MyListener(EventListener):
        def Callback(self, payload):
            print(f'call back with payload {payload}')
    

    listener = MyListener()
    myEvent = Event()
    listener.Subcribe(myEvent)
    myEvent.Emit('{some data}')
