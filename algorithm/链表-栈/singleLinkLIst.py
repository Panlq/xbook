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

    @property
    def length(self):
        count = 0
        cur = self.__head
        while cur != None:
            cur = cur.next
            count += 1
        return count

    def trave(self):
        """遍历链表"""
        cur = self.__head
        while cur != None:
            # print(cur.item, end=' ')
            yield cur.item
            cur = cur.next

    def add(self, item):
        """头部添加元素"""
        node = SingleNode(item)
        node.next, self.__head = self.__head, node

    def append(self, item):
        cur = self.__head
        node = SingleNode(item)
        if self.is_empty():
            cur = node
        else:
            while cur.next != None:
                cur = cur.next
            cur.next = node

    def insert(self, pos, item):
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
        """
        1、要删除的节点是头节点
        2、不是头结点 (需要两个指针)
        """
        cur = self.__head
        pre = None
        while cur != None:
            if cur.item == item:
                # 头结点
                if cur == self.__head:
                    self.__head = cur.next
                else:
                    pre.next = cur.next
                return
            else:
                # 没有找到item
                pre = cur
                cur = cur.next

    def search(self, item):
        """查看节点是否存在"""
        cur = self.__head
        while cur != None:
            if cur.item == item:
                return True
            cur = cur.next
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

    print(t.search('C'))

    t.remove('A')

    print('length', t.length)

    for i in t.trave():
        print(i, end=' ')
    print()