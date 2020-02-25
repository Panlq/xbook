# -*- coding:utf-8 -*-
"""
如何派生内置不可变类型并修改其实例化行为
Numbers, String, Tuple must to override __new__
:https://stackoverflow.com/questions/1565374/subclassing-tuple-with-multiple-init-arguments
"""


class IntTuple(tuple):
    def __new__(cls, iterable):
        g = (i for i in iterable if isinstance(i, int) and i > 0)
        return super(IntTuple, cls).__new__(cls, g)
    
    def __init__(self, iterable):
        pass


if __name__ == '__main__':
    a = ['a', [1,2,3], 1, -1, 0, 4, 9]
    rea = IntTuple(a)
    print(rea)