#!usr/bin/python3
# -*- coding:utf-8 -*-

import time
from datetime import datetime
from eventEngineThreadTimer import EventEngineThreadTimer


def simpleTest(event):
    print(f'Handler A Timer events triggered per second: {str(datetime.now())}')


def test():
    eventEngine = EventEngineThreadTimer()
    eventEngine.registerGeneralHandler(simpleTest)
    eventEngine.start()
    # while True:
    #     time.sleep(1)


if __name__ == '__main__':
    test()
