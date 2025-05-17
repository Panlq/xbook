"""
辗转相除法: 求最大公约数
就是利用分而治之的方法，快速排序的方法
"""

def gcd(a, b):
    while a != 0:
        a, b = b % a, a
    return b


def gcd_recur(a, b):
    """
    greatest common divisor funciton
    """
    if a % b == 0:
        return b
    return gcd_recur(a, a % b)


if __name__ == '__main__':
    print(gcd(1680, 640))
    print(gcd_recur(1680, 640))