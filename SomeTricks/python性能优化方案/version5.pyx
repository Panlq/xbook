# -*- coding: utf-8 -*-
# version5 使用numpy 


import numpy as np


def fib_matrix(n):
    for i in range(n):
        res = pow((np.matrix([[1, 1], [1, 0]], dtype='int64')), i)
        print(int(res[0][0]))