### python 内置装饰器
"""
1. functools.lru_cache 
python 自带模块，实现了备忘录的功能，可以缓存相同的执行结果，做到幂等效果
把耗时操作的结果保存起来，避免传入相同的参数时，重复计算。
least recently used  最近最少使用原则，缓存条目会自动删掉
参数 maxsize 设置保存多少个调用结果
"""
import functools


def trace(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f'{func.__name__} --> {args[0]} --> {result}')
        return result

    return wrapper


@functools.lru_cache()
@trace
def fib(n, a=0):
    if n < 2:
        return n
    return fib(n - 2) + fib(n - 1)


if __name__ == "__main__":
    print(fib(10))
    print(fib(13))
    print(fib(10))
    print(fib(10))
    # 查看缓存的信息
    print(fib.cache_info())