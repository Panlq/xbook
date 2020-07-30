"""
归并排序是采用分治法的一个非常典型的应用。归并排序的思想就是先递归分解数组，再合并数组。

最优时间复杂度：O(nlogn)
最坏时间复杂度：O(nlogn)
稳定性：稳定
"""


def merge_sort(array):
    """归并排序"""
    # 先拆分组
    n = len(array)
    if n <= 1:
        return array

    # 分而治之，两两拆分
    mid = n // 2
    left = merge_sort(array[:mid])
    right = merge_sort(array[mid:])

    return merge(left, right)


def merge(left, right):
    result = []
    left_point, right_point = 0, 0
    # 将两个有序的子序列合并为一个新的整体
    while left_point < len(left) and right_point < len(right):
        if left[left_point] <= right[right_point]:
            result.append(left[left_point])
            left_point += 1
        else:
            result.append(right[right_point])
            right_point += 1

    # 补充列表中剩余的部分
    result += left[left_point:]
    result += right[right_point:]
    return result

if __name__ == '__main__':
    alist = [54,26,93,17,77,31,44,55,20]
    sorted_alist = merge_sort(alist)
    print(sorted_alist)
