
import typing
#### 2. typing
    ## 2.1 typing.TypeVar
    ## 2.2 typing.overload

T = typing.TypeVar('T', int, float, str)

def foo(name: T)-> str:
    print('overload foo ', type(name))
    return 'hello' + str(name)


if __name__ == "__main__":
    foo('1')
    foo(1)
    foo(1.334)