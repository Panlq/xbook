class Node(object):
    """单向链表的结点"""
    def __init__(self, item):
        # item存放数据元素，结点的真正值
        self.item = item
        # 保存指向下一个结点的地址
        self.next = None


class SingleLinkList(object):
    """单向链表的实现"""

    def __init__(self, node=None):
        self.__head = node

    def is_empty(self):
        """链表判空"""
        return self.__head == None

    def length(self):
        """返回链表的长度"""
        # 计数
        count = 0
        # 游标
        cur = self.__head
        while cur != None:
            # 游标右移
            cur = cur.next
            count += 1
        # 跳出循环表示cur指向尾结点
        return count

    def travel(self):
        """遍历链表"""
        cur = self.__head
        while cur != None:
            print(cur.item, end=' ')
            # 游标右移动
            cur = cur.next
        print('')

    def add(self, item):
        """在头部添加元素"""
        # 先创建一个保存item值的结点
        node = Node(item)
        # 将新节点的链接域指向头结点，
        node.next = self.__head
        # 将链表的头_head指向新节点
        self.__head = node

    def append(self, item):
        """在尾部添加元素"""
        # 新结点
        node = Node(item)
        if self.is_empty():
            self.__head = node
        # 链表不为空
        else:
            cur = self.__head
            while cur.next != None:
                cur = cur.next
            # 跳出循环cur指向最后一个结点
            cur.next = node
            node.next = None

    def insert(self, pos, item):
        """指定位置添加元素，要判断插入的位置"""
        if pos <= 0:
            self.add(item)
        elif pos >= self.length():
            self.append(item)
        else:
            # 中间任意位置元素插入
            count = 0
            node = Node(item)
            cur = self.__head
            while count < (pos - 1):
                cur = cur.next
                count += 1
            # 跳出循环时， count = pos -1  cur指向pos前一个结点
            # 新结点next指向pos位置的结点
            node.next = cur.next
            # pos位置前一个结点next指向新的结点
            cur.next = node

    def remove(self, item):
        cur = self.__head
        pre = None
        while cur != None:
            # 找到要删除的元素
            if cur.item == item:
                # 1.要删除的元素是头结点
                if cur == self.__head:
                    self.__head = cur.next
                # 2. 要删除的结点不是头结点
                else:
                    pre.next = cur.next
                return
            # 没有找到要删除的元素 继续移动游标
            else:
                pre = cur
                cur = cur.next
                # 继续寻找要删除的元素

    def search(self, item):
        """链表查找结点是否存在"""
        cur = self.__head
        while cur != None:
            if cur.item == item:
                return True
            cur = cur.next
        # 跳出循环表示还没找到item这结点，不在链表中
        return False

    def pop(self):
        """删除并弹出最后一个元素"""
        cur = self.__head
        pre = None
        count = 0
        if self.length() <= 0:
            print("No element in the stack")
            return
        elif self.length() == 1:
            self.__head = None
        else:
            while count < self.length()-1:
                pre = cur
                cur = cur.next
                count += 1
            pre.next = None
        # 跳出循环cur指向最后一个结点
        return cur.item

    def peek(self):
        """弹出链表第一个元素"""
        cur = self.__head
        self.__head = cur.next
        return cur.item


class Stack(object):
    def __init__(self):
        self.items = SingleLinkList()

    def is_empty(self):
        """判断是否为空"""
        return self.items.is_empty()

    def push(self, item):
        """加入元素"""
        self.items.append(item)

    def pop(self):
        """弹出最后一个元素"""
        return self.items.pop()

    def peek(self):
        """"""
        return self.items.peek()

    def size(self):
        """返回栈的大小"""
        return self.items.length()


if __name__ == "__main__":
    stack = Stack()
    stack.push("hello")
    stack.push("world")
    stack.push("itcast")

    print(stack.size())
    print(stack.peek())
    print(stack.pop())
    print(stack.pop())
    print(stack.pop())
    # print(stack.pop())