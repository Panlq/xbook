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


import time
import functools

t = 0

def trace(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global t
        start = time.time()
        v = func(*args, **kwargs)
        end = time.time()
        print('{}, {}, {}, {}, cost: {} seconds'.format(
                func.__name__, args, kwargs , v, (end - start)))
        t += (end-start)
        return v
    return wrapper


class TimeTrace:
    def __init__(self, f):
        self.f = f
        print(f.__doc__)
       
    def __now(self):
        return time.time()
       
    def __enter__(self):
        self.start = self.__now()
        return self
    
    def __exit__(self, exc_type, exc_val, tb):
        self.end = self.__now()
        print('cost {}'.format(self.end - self.start))
       
    def __call__(self, n):
        start = self.__now()
        val = self.f(n)
        end = self.__now()
        print('{}, {}, {}, cost: {} seconds'.format(self.f.__name__, n , val, (end - start)))
        return val


def fib(n):
    """
    :params n 个数
    :return 当前斐波那契数值
    """
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)


def fib_loop(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
        yield a

class A(object):
    _c = 'test'
    def __init__(self):
        self.x = None

    @property
    def a(self):
        print('using property to access attribute')
        if self.x is None:
            print('return value')
            return 'a'
        else:
            print('error occured')
            raise AttributeError

    @a.setter
    def a(self, value):
        print('setter property val')
        self.x = value

    def __getattribute__(self, name):
        print('using __getattribute__ to access attribute')
        return object.__getattribute__(self, name)

    def __getattr__(self, name):
        print('using __getattr__ to access attribute')
        print('attribute name: ', name)
        return 'b'


if __name__ == '__main__':
    

    # 测试 property, __getattribute__, __getattr__调用顺序
    b = A()
    print(b.a)
    print('-'*50)
    b.a = 10
    print('-'*50)
    print(b.a)
    print('-'*50)
    print(A._c)
    print('-'*50)
    print(b._c)