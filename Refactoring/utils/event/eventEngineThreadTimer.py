#!usr/bin/python3
# -*- coding:utf-8 -*-

import time
from threading import Thread
from eventEngineBase import Event, EventEngineBase
from eventType import EVENT_TIMER


class EventEngineThreadTimer(EventEngineBase):
    def __init__(self):
        EventEngineBase.__init__(self)
        self.__timer = Thread(target=self.__runTimer)
        self.__timerActive = False
        self.__timerSleep = 1

    def timerStart(self):
        self.__timerActive = True
        self.__timer.start()

    def timerStop(self):
        self.__timerActive = False
        self.__timer.join()

    def __runTimer(self):
        while self.__timerActive:
            event = Event(type_=EVENT_TIMER)
            self.put(event)
            time.sleep(self.__timerSleep)