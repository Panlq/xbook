import sys
import warnings
import pdamOld

"""
应用场景: 类似钩子函数
动态给old函数绑定装饰器, 并在实际调用时调用新的API接口
"""


warnings.simplefilter('always')

m = sys.modules['pdamOld']

for t in ['addfunc', 'subfunc']:

    def outer(t=t):

        def wrapper(*args, **kwargs):
            import pdamNew as util
            warnings.warn('pdamOld is deprecated and will be'
                        'removed in a future version, import pdamNew instead',
                        DeprecationWarning, stacklevel=3)
            return getattr(util, t)(*args, **kwargs)
        return wrapper

    setattr(m, t, outer(t))  # duck type dynamic 


if __name__ == '__main__':
    print(pdamOld.addfunc(10, 20))
    print(pdamOld.subfunc(10, 20))