

import time
import threading


def hello(name):
    print(f'hello {name}')
    global timer
    timer = threading.Timer(8.0, hello, ['Jon'])
    timer.start()


if __name__ == '__main__':
    # timer = threading.Timer(8.0, hello, ['Jack'])
    # timer.start()
    hello('Jack')