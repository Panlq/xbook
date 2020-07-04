# 单边队列 只允许一端进，另一端出，线性表 first in first out


class Queue(object):
    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items = []

    def enqueue(self, item):
        """压入队列"""
        self.items.insert(0, item)

    def dequeue(self):
        """出队列"""
        return self.items.pop()

    def size(self):
        return len(self.items)



class DoubleEndedQueue(object):
    """双端队列
    具有队列和栈的性质
    """
    def __init__(self):
        self.items = []
    
    def is_empty(self):
        return self.items = []
    
    def add_front(self, item):
        """队列头部添加元素"""
        self.items.insert(0, item)
    
    def add_rear(self, item):
        """队列尾部添加元素"""
        self.items.append(item)

    def remove_front(self):
        return self.items.pop(0)

    def remove_rear(self):
        return self.items.pop()

    def size(self):
        return len(self.items)
