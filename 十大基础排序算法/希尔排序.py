"""
希尔排序 （shell sort）
是插入排序的一种，缩小增量排序 
思想: 将数据组列在一个表中并对列分别进行插入排序，重复这个过程，不过每次用更长的列（步长更长了，列数更少了）来进行
最后整个表就只有一列了

最优时间复杂度：根据步长序列的不同而不同
最坏时间复杂度：O(n2)
稳定性：不稳定

"""


def shell_sort(array):
    n = len(array)
    # 初始步长
    gap = n // 2
    while gap >= 1:
        # 控制从gap到最后一个元素都需要进行插入排序
        for i in range(gap, n):
            while i >= gap and array[i] < array[i - gap]:
                array[i], array[i - gap] = array[i - gap], array[i]
                i = i - gap

        # 获取新的步长
        gap //= 2



alist = [54, 26, 93, 17, 77, 31, 44, 55, 20]
shell_sort(alist)
print(alist)
