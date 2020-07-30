"""
用列表实现栈

Stack() 创建一个新的空栈
push(item) 添加一个新的元素item到栈顶
pop() 弹出栈顶元素
peek() 返回栈顶元素
is_empty() 判断栈是否为空
size() 返回栈的元素个数
"""


class Stack(object):
    """栈"""

    def __init__(self):
        """初始化一个空栈"""
        self.items = []

    def push(self, item):
        """添加一个新的元素item到栈顶"""
        # self.items.insert(0, item)  # 时间复杂度 O(N)
        self.items.append(item)       # 时间复杂度 O(1)

    def pop(self):
        """弹出栈顶元素, 并删除"""
        # return self.items.pop(0)
        try:
            return self.items.pop()
        except Exception as e:
            print("not pop from empty", e)

    def peek(self):
        """返回栈顶元素"""
        return self.items[len(self.items) - 1]
        # return self.items[-1]

    def is_empty(self):
        """判断栈是否为空"""
        return self.items == []

    def size(self):
        """返回栈的元素个数"""
        return len(self.items)


if __name__ == "__main__":
    stack = Stack()