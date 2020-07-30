# coding=utf8

"""
左节点: 2 * i + 1
右节点: 2 * i + 2
父节点: (i - 1)>>1

二叉堆: 完全二叉树
大根堆: 每个节点的值都大于或等于左右子节点
有问题,需调整

参考: https://blog.csdn.net/yuhentian/article/details/80159284
参考: https://juejin.im/post/5c0f9c1fe51d451ac27c470a
"""


class MaxHeap(object):
    def __init__(self):
        self._data = []

    @property
    def size(self):
        return len(self._data)

    def is_empty(self):
        return self.size == 0

    def add(self, item):
        # 插入元素 入堆
        self._data.append(item)
        self.__shift_up()

    def pop(self):
        # 出堆
        if self.size > 0:
            ret = self._data[0]
            # pop 堆顶 元素 ，从堆尾拿元素占位堆顶
            self._data[0] = self._data[self.size - 1]
            # 重新调整堆结构，下移
            self.__shift_down()
            return ret

    def travel(self):
        return self._data

    def __shift_up(self):
        # 重新调整堆结构，即判断该元素是否大于父节点，如果比父节点大就替换，不考虑兄弟元素
        # 并循环 比较其父元素
        index = self.size - 1
        parent = (index - 1) >> 1  # 找到其父节点的公式
        while index > 0 and self._data[parent] < self._data[index]:
            # 替换元素
            self._data[parent], self._data[index] = self._data[index], self._data[parent]
            index = parent
            parent = (index - 1) >> 1

    def __shift_down(self):
        # 下移的都是0节点，使它不小于子节点
        index = 0
        child_index = (index << 1) + 1
        while child_index < self.size:
            if child_index + 1 < self.size and self._data[child_index + 1] > self._data[child_index]:
                # 判断是否有右节点，有右节点，并且右节点较大的时候就讲该元素 放入右子树去循环下移
                child_index += 1
            if self._data[index] >= self._data[child_index]:
                # 堆的索引位置已经大于或等于两个子节点了，不需要交换了
                break

            self._data[index], self._data[child_index] = self._data[child_index], self._data[index]
            index = child_index
            child_index = (index << 1) + 1


if __name__ == '__main__':
    import random

    h = MaxHeap()
    alist = list(range(10))
    random.shuffle(alist)
    print(alist)
    for i in alist:
        h.add(i)

    print(h.travel())