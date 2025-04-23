#!usr/bin/python3
# -*- coding:utf-8 -*-


import time
import traceback
from threading import Thread


class CountDown(Thread):
    def __init__(self):
        super(CountDown, self).__init__()
        self.exitcode = 0
        self.exception = None
        self.exc_traceback = ''

    def run(self):
        try:
            self._run()
        except Exception as e:
            self.exitcode = 1
            self.exception = e
            self.exc_traceback = traceback.format_exc()

    def _run(self):
        num = 100
        print('slave start')
        for i in range(5, -1, -1):
            print('Num: {0}'.format(num/i))
            time.sleep(1)
        print('slave end')


if __name__ == '__main__':
    print('main start')
    td = CountDown()
    td.start()
    td.join()
    if td.exitcode != 0:
        print('Exception in' + td.getName() + ' catch by main')
        print(td.exc_traceback)
    print('main end')
