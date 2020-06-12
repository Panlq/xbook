"""
Python Cookbood 9.13
"""


## 禁止类实例化，
class NoInstances(type):
    def __call__(self, *args, **kwargs):
        raise TypeError("Can't instantiate directly")


class Spam(metaclass=NoInstances):
    @staticmethod
    def grox(x):
        print('Span.grok value is', x)



# 2. 实现单利模式
class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instalce = super().__call__(*args, **kwargs)
        else:
            return self.__instance

        
class Spam2(metaclass=Singleton):
    def __init__(self):
        print('Creatin single spam')


    
## 实现缓存实例

import weakref


class Cached(type):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__cache = weakref.WeakValueDictionary()

    def __call__(self, *args):
        if args in self.__cache:
            return self.__cache[args]
        else:
            obj = super().__call__(*args)
            self.__cache[args] = obj
            return obj
    
class Spam3(metaclass=Cached):
    def __init__(self, name):
        print('Creating Spam(!r:)'.format(name))
        self.name = name


a = Spam3('Guido')
b = Spam3('Diana')
c = Spam3('Guido')