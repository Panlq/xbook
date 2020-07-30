"""
双向链表

is_empty() 链表是否为空
length() 链表长度
travel() 遍历链表
add(item) 链表头部添加
append(item) 链表尾部添加
insert(pos, item) 指定位置添加
remove(item) 删除节点
search(item) 查找节点是否存在
"""


class Node(object):
    """单向链表的结点"""
    def __init__(self, item):
        # item存放数据元素，结点的真正值
        self.item = item
        # 保存指向下一个结点的地址
        self.next = None
        # 前一个结点的地址
        self.prev = None


class DoubleLinkList(object):

    def __init__(self):
        self.__head = None

    def is_empty(self):
        """判断链表是否为空"""
        return self.__head == None

    def length(self):
        """返回列表长度"""
        cur = self.__head
        count = 0
        while cur != None:
            count += 1
            cur = cur.next
        return count

    def travel(self):
        """遍历链表"""
        cur = self.__head
        while cur != None:
            print(cur.item, end=" ")
            cur = cur.next

        print('')

    def add(self,item):
        """头部插入元素"""
        node = Node(item)
        if self.is_empty():
            # 如果是
            self.__head = node
        else:
            # 新结点的next指向之前的头结点
            node.next = self.__head
            # 老的头结点的pre指向新的头结点
            self.__head.prev = node
            # 将头指针指向新的头结点
            self.__head = node

    def append(self, item):
        """尾部添加结点"""
        node = Node(item)
        cur = self.__head
        while cur.next != None:
            cur = cur.next
        # 跳出循环cur指向最后一个结点
        cur.next = node
        # 新结点的prev指向最后一个结点
        node.prev = cur

    def insert(self, pos, item):
        """指定位置添加元素"""
        if pos <= 0:
            self.add(item)
        elif pos >= self.length():
            self.append(item)
        else:
            # 中间任意位置元素插入
            count = 0
            cur = self.__head
            node = Node(item)
            while count < pos:
                # 游标右移
                cur = cur.next
                count += 1
            # 跳出循环的时候 count == pos cur指向pos当前结点
            node.next = cur
            node.prev = cur.prev
            cur.prev.next = node
            cur.prev = node

    def remove(self, item):
        """删除指定结点"""
        cur = self.__head

        while cur != None:
            # 找到了要删除的元素
            if cur.item == item:
                # 1. 要删除的元素是头结点
                if cur == self.__head:
                    self.__head = cur.next
                    # 判断是否有下一个结点
                    if cur.next:
                        cur.next.prev = None
                # 2. 要删除的结点不是头结点
                else:
                    cur.prev.next = cur.next
                    if cur.next:
                        cur.next.prev = cur.prev
                return
            else: # 没有找到要删除的元素，继续移动游标
                cur = cur.next

    def search(self, item):
        """查找结点是否存在于链表中"""
        # 当前游标在开头
        cur = self.__head
        while cur != None:
            # 搜索到了该元素
            if cur.item == item:
                return True
            else:
                cur = cur.next
        # 跳出循环表示没有找到item结点，
        return False


if __name__ == "__main__":
    ll = DoubleLinkList()
    ll.add("curry")
    ll.add("james")
    ll.append("harden")
    ll.insert(2, "durant")

    print("length: %d" % ll.length())
    ll.travel()

    ll.remove("durant")
    print("length: %d" % ll.length())
    ll.travel()

    print(ll.search("curry"))