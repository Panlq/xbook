# first in last out


class Stack(object):
    def __init__(self):
        self.items = []
    
    def is_empty():
        return self.items == []
    
    def push(self, item):
        self.items.append(item)

    def pop(self):
        self.items.pop()
    
    def peek(self):
        """返回栈顶元素"""
        return self.items[-1]

    def size(self):
        return len(self.items)
