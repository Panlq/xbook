import typing

"""
The @overload-decorated definitions are for the benefit of the type checker only, 
since they will be overwritten by the non-@overload-decorated definition, 
while the latter is used at runtime but should be ignored by a type checker
"""


@typing.overload
def foo(name: str)-> str:
    print('overload foo ', type(name))


@typing.overload
def foo(name: float)-> float:
    print('overload foo ', type(name))


@typing.overload
def foo(name: int)-> str:
    print('overload foo ', type(name))


@typing.overload
def foo(name: str, age: int)-> str:
    print('overload foo ', type(name), type(age))


def foo(name, age=14):
    print("overload foo", type(name), type(age))

if __name__ == "__main__":
    foo(2)
    foo("2")
    foo(2.34)
    foo("pan", 23)