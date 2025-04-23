
"""
 警告消息通常写入 sys.stderr
 警告过滤器可以用来控制是否发出警告信息, 是一些匹配规则和动作的序列
 reference: http://blog.konghy.cn/2017/12/16/python-warnings/
"""

import warnings
import functools


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)   # turn off filter
        warnings.warn(f'Call to deprecated function {func.__name__}', category=DeprecationWarning, stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    return wrapper


# Example
@deprecated
def oldAdd(a, b):
    return a + b


class SomeClass(object):
    @deprecated
    def someOldFunc(self, x, y):
        return x + y


if __name__ == '__main__':
    print(oldAdd(1, 2))