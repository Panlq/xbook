## 单向链表的实现
# 抽象数据类型 Abstract Data Type
# 插入，删除，修改，查找，排序


class SingleNode(object):
    """node"""

    def __init__(self, item):
        self.item = item
        self.next = None


class SingleLinkList(object):
    def __init__(self):
        self.__head = None

    def is_empty(self):
        return self.__head == None

    def closedLoop(self):
        pass

    def getRearNode(self):
        cur = self.__head
        while cur.next != self.__head:
            cur = cur.next
        return cur

    @property
    def length(self):
        count = 0
        # 如果链表为空,返回长度为0
        if self.is_empty():
            return count
        cur = self.__head
        while cur.next != self.__head:
            count += 1
            cur = cur.next
        return count + 1

    def trave(self):
        """遍历链表"""
        cur = self.__head
        while cur.next != self.__head:
            # print(cur.item, end=' ')
            yield cur.item
            cur = cur.next
        # 返回最后一个
        yield cur.item

    def add(self, item):
        """头部添加元素"""
        node = SingleNode(item)
        if self.is_empty():
            self.__head = node
            node.next = self.__head
        else:
            node.next = self.__head
            # 游标指向链表尾部，将尾部节点next指向node
            rear = self.getRearNode()
            rear.next = node
            # head 指向node
            self.__head = node

    def append(self, item):
        """尾部添加节点"""
        node = SingleNode(item)
        if self.is_empty():
            self.__head = node
            node.next = self.__head
        else:
            rear = self.getRearNode()
            # 尾部节点指向node
            rear.next = node
            # node 指向 head
            node.next = self.__head

    def insert(self, pos, item):
        """指定位置插入节点，不影响首位节点，所以跟单向链表一样"""
        if pos <= 0:
            self.add(item)
        elif pos > self.length - 1:
            self.append(item)
        else:
            cur = self.__head
            node = SingleNode(item)
            for _ in range(pos - 1):
                cur = cur.next
            node.next, cur.next = cur.next, node

    def remove(self, item):
        if self.is_empty():
            return
        cur = self.__head
        pre = None
        while cur.next != self.__head:
            if cur.item == item:
                # 判断是否是头结点
                if cur == self.__head:
                    # 获取尾节点
                    rear = self.getRearNode()
                    self.__head = cur.next
                    rear.next = self.__head
                else:
                    # 中间节点
                    pre.next = cur.next
                return
            else:
                # 没有找到item
                pre = cur
                cur = cur.next
        # 退出循环，此时cur指向尾节点，判断是否要删除尾节点
        if cur.item == item:
            if cur == self.__head:
                # 链表只有一个节点
                self.__head = None
            else:
                pre.next = self.__head
        # 没有该节点
        pass

    def search(self, item):
        """查看节点是否存在"""
        if self.is_empty():
            return False
        cur = self.__head
        while cur.next != self.__head:
            if cur.item == item:
                return True
            cur = cur.next
        # 检查最后一个
        if cur.item == item:
            return True
        return False


if __name__ == '__main__':
    t = SingleLinkList()
    t.add('A')
    t.add('B')
    t.append('C')
    t.insert(2, 'D')
    print('length', t.length)

    for i in t.trave():
        print(i, end=' ')
    print()

    print(t.search('B'))

    t.remove('C')

    print('length', t.length)

    for i in t.trave():
        print(i, end=' ')
    print()