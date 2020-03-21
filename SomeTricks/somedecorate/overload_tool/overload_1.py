import functools
import typing

#### 1. singledispatch
"""
支持方法重载， 将普通的函数变为泛函数 (generic function)
"""

# eg:
@functools.singledispatch
def typecheck():
    pass


@typecheck.register(str)
def _(text):
    print(type(text))
    print('str')


@typecheck.register(list)
def _(text):
    print(type(text))
    print('list')


@typecheck.register(int)
def _(text):
    print(type(text))
    print('int')


@typecheck.register(float)
def _(text):
    print(type(text))
    print('float')


if __name__ == "__main__":
    typecheck('1')
    typecheck(1)
    typecheck(1.334)