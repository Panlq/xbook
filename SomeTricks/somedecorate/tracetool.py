# -*- coding: utf-8 -*-

import sys, os, linecache
from functools import wraps


def trace(func):
    def globaltrace(frame, why, arg):
        if why == 'call': return localtrace
        return None

    def localtrace(frame, why, arg):
        if why == 'line':
            # record the file name and line number of every trace
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            bname = os.path.basename(filename)
            print('{} ({}): {}'.format(bname, lineno, linecache.getline(filename, lineno).strip(r"\r\n")))
 
        return localtrace
    
    def _f(*args, **kwargs):
        sys.settrace(globaltrace)
        result = func(*args, **kwargs)
        sys.settrace(None)
        return result
    return _f


@trace
def foo(a, b):
    print(a * b)
    return (a * b)


def tracefun(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        import sys
        frame = sys._getframe()
        filename = frame.f_back.f_code.co_filename
        lineno = frame.f_back.f_lineno
        print('#'*20)
        print(f'caller filename:{filename}')
        print(f'caller lineno: {lineno}')
        print('#'*20)
        func(*args, **kwargs)

    return wrapper


class A:
    def __init__(self):
        self.container = []

    @tracefun
    def put(self, item):
        self.container.append(item)



@tracefun
def add(a, b):
    print(a+b)


def fun2(a, b):
    print(add(a, b))



if __name__ == '__main__':
    foo(2, 7)
    add(15, 12)
    a = A()
    a.put(14)
    