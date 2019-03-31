"""
思想：升序排序
1、根据无序序列，构建一个最大堆
    根据最大堆的定义，每个节点的值都大于或等于左右子节点
    从数组中选出有有子节点的元素(满足 n // 2) 因为是二叉树，所以最大度是2，比如有9个元素的元组，可以求得，有自子节点的只有前4个元素满足
    在对前4个元素进行判断
        假设第0 个位跟节点，与他的左右节点进行比较， 如果比较有更大值，就进行交换，在重复执行剩下的元素判断，最后得到一个最大堆
        left: 2 * i + 1  当然长度不能超多元组的长度
        right: 2 * i + 2 
2、进行堆排序
    堆顶肯定是最大的元素，每次将堆顶元素即数组的第0个元素，与叶子节点最右一个节点即元组最后一个节点替换，就把最大元素放在最右端了，
    然后再对剩下的元组（每次长度减1）重新调整为最大堆，再继续堆顶与堆尾的替换，以此往复，最后便可得到升序排序结果

时间复杂度:
    最差/平均/最优时间复杂度：O(nlgn)
空间复杂度: O(1), in-place排序
稳定性: 不稳定


参考：https://ictar.xyz/2015/12/07/九大排序算法及其Python实现之堆排序/
"""


heap_size = 0
LEFT = lambda i: 2 * i + 1
RIGHT = lambda i: 2 * i + 2

# 维护最大堆
# def keep_max_heap(array, i):
#     l, r = LEFT(i), RIGHT(i)
#     largest = l if l < heap_size and array[l] > array[i] else i
#     largest = r if r < heap_size and array[r] > a[largest] else largest
#     if i != largest:
#         array[i], array[largest] = array[largest], array[i]
#         keep_max_heap(array, largest)

class Heap(object):
    def __init__(slef, type_ = 'max'):
        self.type_ = type_
        self.left = lambda i: 2 * i + 1
        self.right = lambda i: 2 * i + 2

    def heap_adjust(self, array, pos, heap_size):
        while True:
            l, r = self.left(pos), self.right(pos)
            largest = l if l < heap_size and array[l] > array[i] else i
            largest = r if r < heap_size and array[r] > array[largest] else largest
            if i == largest: break
            array[i], array[largest] = array[largest], array[i]
            i = largest

    @staticmethod
    def buile_heap(array):
        heap_size = len(array)
        # 根据有子节点的数据量去构建堆
        for i in range(len(array) // 2 - 1, -1, -1):
            heap_adjust(array, i, heap_size)
    # TODO: 不要硬编码


# 维护最大堆
def keep_max_heap(array, i):
    while True:
        l, r = LEFT(i), RIGHT(i)
        largest = l if l < heap_size and array[l] > array[i] else i
        largest = r if r < heap_size and array[r] > array[largest] else largest
        if i == largest: break
        array[i], array[largest] = array[largest], array[i]
        i = largest


# 构建最大堆
def build_max_heap(array):
    global heap_size
    heap_size = len(array)
    # 根据有子节点的数据量去构建堆
    for i in range(len(array) // 2 - 1, -1, -1):
        keep_max_heap(array, i)


# 堆排序
def heap_sort(array):
    global heap_size
    build_max_heap(array)
    for i in range(len(array)-1, -1, -1):
        array[i], array[0] = array[0], array[i]
        heap_size -= 1
        keep_max_heap(array, 0)



if __name__ == '__main__':
    alist = [54, 26, 93, 17, 77, 31, 44, 55, 20]
    heap_sort(alist)
    print(alist)
