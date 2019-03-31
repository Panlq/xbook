# coding=utf8

import time
import functools

# 计时装饰器

def costTimer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.clock()
        func(*args, **kwargs)
        end = time.clock()
        print(f'cost: {end - start} seconds')
    return wrapper