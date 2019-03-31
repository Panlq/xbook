"""
Bubble Sort

比较相邻的元素， 如果第一个比第二个大(升序)， 交换他们
对每个相邻元素做同样的工作，从开始第一对到结尾的最后一对，知道最后最后一个元素就是最大的

针对所有的元素重复以上步骤，处理最后一个
持续每次对原来与少的元素重复上面步骤，直到没有任何一对数据需要比较

"""
from common import costTimer


@costTimer
def bubble_sort(array):
    length = len(array)
    for i in range(length):
        for j in range(length - i - 1):
            if array[j] > array[j+1]:
                array[j], array[j+1] = array[j+1], array[j]


# 优化1， 如果列表本身就是有序的在第一次循环时就跳出
@costTimer
def bubble_sort2(array):
    length = len(array)
    for i in range(length):
        flag = False
        for j in range(length - i - 1):
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]
                flag = True
        if not flag:
            break


# 优化2 双向冒泡 鸡尾酒排序，因为未发生交换操作的区域是有序的，故每轮扫描下来可以更新上下边界，减少扫描范围
@costTimer
def bubble_sort3(array):
    low, high = 0, len(array) - 1
    while low < high:
        swapPos = low
        for i in range(low, high):
            if array[i] > array[i+1]:
                array[i], array[i+1] = array[i+1], array[i]
                swapPos = i
        high = swapPos  #修改待排序数组的上界为最后一次发生交换操作的位置
        for j in range(high, low, -1):  #逆序扫描A[low+1..high]
            if array[j] < array[i-1]:
                array[j], array[j-1] = array[j-1], array[j]
                swapPos = j
        low = swapPos  #修改待排序数组的下界为最后一次发生交换操作的位置





if __name__ == '__main__':
    import random
    a = list(range(1,1000))
    random.shuffle(a)
    # print(a)

    # bubble_sort(a)
    # print(a)

    # bubble_sort2(a)
    # print(a)

    bubble_sort3(a)
    # print(a)
