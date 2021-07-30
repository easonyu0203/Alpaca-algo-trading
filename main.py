from logging import log
from typing import Tuple
from dotenv import load_dotenv; load_dotenv()
import os
from time import sleep
import subprocess

from Backend.Event import Event
from MyAlgo import MyAlogo

position_history_path = os.environ.get('Position_History_Path')
log_path = os.environ.get('Log_Path')

def LiveTrading():
    my_algo = MyAlogo(log=True, debug_log=True)
    my_algo.Initialize()

    my_algo.Stream_data.Start_listen_stream_data(my_algo.subscribe_symbol_set)
    #main loop
    while True:
        #check market status to connect or disconnect Alpaca streaming
        my_algo._check_for_listening_stream_data()

        #check emit data in event or not
        my_algo.Stream_data.Check_DataIn_Event()

        #handle event that have emit
        Event._event_loop()

        sleep(1.0)

def Backtesting():
    my_algo = MyAlogo(log=True, debug_log=True)


def clear_log_files():
    subprocess.run(['rm',position_history_path])
    subprocess.run(['rm', log_path])


if __name__ == '__main__':
    clear_log_files()
    LiveTrading()