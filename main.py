from time import sleep

from Backend.Event import Event
from Backend.MarketStatus import MarketStatus
from MyAlgo import MyAlogo

def main():
    my_algo = MyAlogo(log=True)
    my_algo.Initialize()

    my_algo.Stream_data.Start_listen_stream_data(my_algo.subscribe_symbol_set)
    #main loop
    while True:
        my_algo._check_for_listening_stream_data()

        my_algo.Stream_data.Check_DataIn_Event()

        Event._event_loop()

        sleep(1.0)




if __name__ == '__main__':
    main()