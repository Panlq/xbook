
"""
单向循环链表

is_empty() 判断链表是否为空
length() 返回链表的长度
travel() 遍历
add(item) 在头部添加一个节点
append(item) 在尾部添加一个节点
insert(pos, item) 在指定位置pos添加节点
remove(item) 删除一个节点
search(item) 查找节点是否存在
"""


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
        if self.is_empty():
            return 0
        # 长度计数
        count = 1
        # 游标
        cur = self.__head
        while cur.next != self.__head:
            # 游标右移
            cur = cur.next
            count += 1
        # 跳出循环表示cur指向尾结点，cur.next指向头结点
        return count

    def travel(self):
        """遍历链表"""
        cur = self.__head
        while cur.next != self.__head:
            print(cur.item, end=' ')
            # 游标右移动
            cur = cur.next
        # 跳出循环的时候最后一个结点还未打印
        print(cur.item)

    def add(self, item):
        """在头部添加元素"""
        # 先创建一个保存item值的结点
        node = Node(item)
        # 链表为空
        if self.is_empty():
            self.__head = node
            # 将新节点的next指向自己，形成环
            node.next = node
        else:
            cur = self.__head
            while cur.next != self.__head:
                cur = cur.next
            # 跳出循环cur指向最后一个结点
            # 将新节点的链接域指向头结点，
            node.next = self.__head
            # 将链表的头_head指向新节点
            self.__head = node
            cur.next = self.__head

    def append(self, item):
        """在尾部添加元素"""
        # 新结点
        node = Node(item)
        if self.is_empty():
            self.add(item)
        # 链表不为空
        else:
            cur = self.__head
            while cur.next != self.__head:
                cur = cur.next
            # 跳出循环cur指向最后一个结点
            cur.next = node
            node.next = self.__head

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
        """删除元素操作"""
        if self.is_empty():
            return
        cur = self.__head
        pre = None
        while cur.next != self.__head:
            # 找到了要删除的元素
            if cur.item == item:
                # 1. 要删除的元素是头结点
                if cur == self.__head:
                    rear = self.__head
                    while rear.next != self.__head:
                        rear = rear.next
                    # 跳出循环 rear游标指向最后一个结点
                    self.__head = cur.next
                    rear.next = self.__head
                # 2.要删除的结点不是头结点
                else:
                    pre.next = cur.next
                return
            # 没有找到要删除的元素 继续移动游标
            else:
                pre = cur
                cur = cur.next
        # 跳出循环表示已经到了最后一个结点，cur指向最后一个结点，pre指向倒数第二个结点
        # 判断最后一个结点是否需要删除
        if cur.item == item:
            if cur == self.__head:
                # 链表只有一个结点，删除仅有的这个结点
                self.__head = None
            else:
                pre.next = self.__head

    def search(self, item):
        """链表查找结点是否存在"""
        cur = self.__head
        while cur != None:
            if cur.item == item:
                return True
            cur = cur.next
        # 跳出循环表示还没找到item这结点，不在链表中
        return False


if __name__ == "__main__":
    ll = SingleLinkList()
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