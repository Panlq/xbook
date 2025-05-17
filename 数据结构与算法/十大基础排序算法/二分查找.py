"""
### 二分查找
二分查找又称折半查找，优点是比较次数少，查找速度快，平均性能好；其缺点是要求待查表为有序表，且插入删除困难。因此，折半查找方法适用于不经常变动而查找频繁的有序列表

最优时间复杂度：O(1)
最坏时间复杂度：O(logn)
"""


def binary_search_recursion(array, item):
    """折半查找，递归版本"""
    n = len(array)
    mid = n // 2

    if item == array[mid]:
        return True
    elif item < array[mid]:
        return binary_search(array[:mid], item)
    else:
        return binary_search(array[mid:], item)


    
def binary_search(array, item):
    """折半查找，非递归版本"""
    start = 0
    end = len(array)

    while start <= end:
        mid = (start + end) // 2
        if item == array[mid]:
            return True
        elif item < array[mid]:
            end = mid - 1
        else:
            start = mid + 1
    # start > end
    return False



if __name__ == '__main__':
    testlist = [0, 1, 2, 8, 13, 17, 19, 32, 42]
    print(binary_search_recursion(testlist, 3))
    print(binary_search_recursion(testlist, 13))

    print(binary_search(testlist, 3))
    print(binary_search(testlist, 13))