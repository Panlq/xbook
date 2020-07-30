"""
快速排序：划分交换排序

1. 选择基准值 pivot
2. 分区操作：所有元素比基准值小的摆放在基准值前面，所有元素比基准大的摆在基准值后面，分区结束后基准值就在中间位置
3. 递归地把小于基准值元素的子数列和大于基准值元素的子数列排序

最优时间复杂度：O(nlogn)
最坏时间复杂度：O(n2)
稳定性：不稳定
"""


def quick_sort(array):
    if len(array) < 2:
        return array
    else:
        pivot = array[0] #将0元素作为基准值，
        # 所有小于基准值的元素组成在子数组
        less = [i for i in array[1:] if i <= pivot]
        # 所有大于基准值的元素组成的子数组
        greater = [i for i in array[1:] if i > pivot]

        return quick_sort(less) + [pivot] + quick_sort(greater)


def quick_sort2(array, start, end):
    """
    Time Complexity: 
    最优时间复杂度 O(nlogn)
    最坏时间复杂度 O(n^2)
    稳定性: 不稳定
    空间复杂度 O(1)
    """
    # 递归退出条件
    if start >= end:
        return

    # 定义基准值
    mid = array[start]
    low = start
    high = end

    while low < high:
        # 如果low 与 high 未重合，high指向的元素不比基准值小，则high想左移动
        while low < high and array[high] >= mid:
            high -= 1
        # 找到一个比基准值小的元素，交换到低位去
        array[low] = array[high]

        while low < high and array[low] < mid:
            low += 1
        # 找到一个比基准值大的元素，交换到高位去
        array[high] = array[low]

    # 退出循环后 low与high 重合，此时所指位置为基准元素的正确位置
    array[low] = mid

    # 对基准元素左右边的子序列进行快速排序
    quick_sort2(array, start, low-1)

    # 对基准值元素右边的子序列进行快速排序
    quick_sort2(array, low+1, end)


alist = [54, 26, 93, 17, 77, 31, 44, 55, 20]
# quick_sort2(alist, 0, len(alist)-1)
alist = quick_sort(alist)
print(alist)