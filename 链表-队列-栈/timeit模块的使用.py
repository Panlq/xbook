"""

使用timeit模块测试代码块的执行速度
"""


def t1():
    l = []
    for i in range(1000):
        l = l + [i]


def t2():
    l = []
    for i in range(1000):
        l.append(i)


# 列表推导式
def t3():
    l = [i for i in range(1000)]


# 强制类型转换
def t4():
    l = list(range(1000))


from timeit import Timer


# timer1 = Timer('t1()', 'from __main__ import t1')
# print('concat', timer1.timeit(number=1000), 'seconds')
#
# timer2 = Timer('t2()', 'from __main__ import t2')
# print('concat', timer2.timeit(number=1000), 'seconds')
#
# timer3 = Timer('t3()', 'from __main__ import t3')
# print('concat', timer3.timeit(number=1000), 'seconds')
#
# timer4 = Timer('t4()', 'from __main__ import t4')
# print('concat', timer4.timeit(number=1000), 'seconds')


x = range(20000)
pop_zero = Timer("list(x).pop(0)", "from __main__ import x")
print("pop_zero", pop_zero.timeit(number=1000), 'seconds')


b = range(20000)
pop_end = Timer("list(b).pop()", "from __main__ import b")
print("pop_end", pop_end.timeit(number=1000), 'seconds')