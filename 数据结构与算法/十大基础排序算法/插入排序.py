"""
插入排序（内部排序）（Insertion Sort)
构建有序序列，对于未排序数据，在已排序序列中从后向前扫描，找到相应位置并插入。
从后向前扫描过程中，需要反复把已排序元素逐步向后挪位，

选择排序是对无序数据遍历去最小值进行排序操作，无序选择最小
插入排序是将无序数据与初始构建的有序序列对比来实现排序，有序冒泡

"""

def insert_sort(array):
    """
    Timer Complexity: O(n^2)
    """
    # 从第二个位置，开始向前插入
    for i in range(1, len(array)):
        # 从第i 个元素开始向前比较，如果小于前一个，交换位置
        for j in range(i, 0, -1):
            if array[j] < array[j - 1]:
                array[j], array[j-1] = array[j-1], array[j]


alist = [54, 26, 93, 17, 77, 31, 44, 55, 20]
insert_sort(alist)
print(alist)