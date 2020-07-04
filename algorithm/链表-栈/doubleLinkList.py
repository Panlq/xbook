class Node(object):
    def __init__(self, item):
        self.item = item
        self.next = None
        self.prev = None


class DoubleLinkList(object):
    def __init__(self):
        self.__head = None

    def is_empty(self):
        return self.__head == None

    @property
    def length(self):
        cur = self.__head
        count = 0
        while cur != None:
            count += 1
            cur = cur.next
        return count

    def travel(self):
        cur = self.__head
        while cur != None:
            yield cur.item
            cur = cur.next

    def add(self, item):
        node = Node(item)
        if self.is_empty():
            self.__head = node
        else:
            node.next = self.__head
            self.__head.prev = node
            self.__head = node

    def append(self, item):
        node = Node(item)
        if self.is_empty():
            self.__head = node
        else:
            cur = self.__head
            while cur.next != None:
                cur = cur.next
            cur.next = node
            node.prev = cur

    def search(self, item):
        cur = self.__head
        while cur != None:
            if cur.item == item:
                return True
            cur = cur.next
        return False

    def insert(self, pos, item):
        if pos <= 0:
            self.add(item)
        elif pos > self.length - 1:
            self.append(item)
        else:
            node = Node(item)
            cur = self.__head
            for _ in range(pos - 1):
                cur = cur.next
            node.prev = cur
            node.next = cur.next
            cur.next.prev = node
            cur.next = node

    def remove(self, item):
        """
        删除元素：考虑是否是头结点，是否有子节点
        """
        cur = self.__head
        while cur != None:
            if cur.item == item:
                if cur == self.__head:
                    self.__head = cur.next
                    if cur.next:
                        # 如果有子节点，子节点prev -> None
                        cur.next.prev = None
                else:
                    cur.prev.next = cur.next
                    if cur.next:
                        cur.next.prev = cur.prev
                break
            else:
                cur = cur.next


if __name__ == '__main__':
    t = DoubleLinkList()
    t.add('A')
    t.add('B')
    t.append('C')
    print('length', t.length)

    for i in t.travel():
        print(i, end=' ')

    t.insert(2, 'D')
    print()
    print('length', t.length)

    for i in t.travel():
        print(i, end=' ')
    print()

    print(t.search('A'))
    print(t.search('lj'))

    t.remove('B')

    for i in t.tSravel():
        print(i, end=' ')
    print()