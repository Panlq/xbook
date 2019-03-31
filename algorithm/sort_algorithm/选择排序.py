"""
首先在未排序序列中找到最小（大）元素，存放在排序序列的起始位置
然后再从剩余的未排序的元素继中继续寻找最小（大）元素放在已排序序列末尾

"""


def selection_sort(array):
    """
    Time Complexity: O(n^2)
    稳定性：不稳定
    """
    n = len(array)
    for i in range(n - 1):
        # 有一个指针记录最小值位置
        min_index = i
        # 从 i+1 到末尾选出最小值
        for j in range(i+1, n):
            if array[j] < array[min_index]:
                min_index = j

        # 如果选择出的数据不在正确位置，进行交换
        if min_index != i:
            array[i], array[min_index] = array[min_index], array[i]



alist = [54, 226, 93, 17, 77, 31, 44, 55, 20]
selection_sort(alist)
print(alist)