
#!/usr/bin/python3
# -*- coding: utf-8 -*-
# __author__ = '__JonPan__'

"""
参考来源：https://blog.csdn.net/jiangbo721/article/details/106336940?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-1.compare&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-1.compare
"""

from math import log
from random import random, seed

class Node(object):
    def __init__(self, key, level):
        self.key = key

        # 当前节点的指向下一个节点，用列表维护对应的层数，列表的索引是层数, 对象是节点
        self.forward = [None] * (level + 1)
    
    def __str__(self):
        return f'Node({str(self.key)})'

    
class SkipList(object):
    def __init__(self, expected_size=8000, p=0.25):
        self.max_level = int(log(expected_size, 2) + 1)
        self.p = p      # 抛硬币的建层概率
        self.header = Node(-1, self.max_level)
        self.level = 0
        self.size = 0

    def random_level(self):
        lev = 0
        while random() < self.p and lev < self.max_level:
            lev += 1
        
        return lev
    
    def insert(self, key):
        update = [None] *(self.max_level + 1)
        current = self.header
        """
        从跳越列表的最高层开始向后移动当前引用
        当要插入的键大于当前节点旁边的键值时，向后移动当前引用
        否则在 update 中插入当前值，向下移动一层并继续搜索
        """
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current
        
        current = current.forward[0]


        """
        如果 current 是 NULL 意味着我们已经到达了列表尾部或当前节点和要插入的节点值不一样, 我们要在 update[0] 和 current 之间插入
        """
        if current is None or current.key != key:
            # 为节点随机生成层数
            rlevel = self.random_level()

            # 如果超过当前层, 补全中间层
            if rlevel > self.level:
                for i in range(self.level + 1, rlevel + 1):
                    update[i] = self.header
                # 更新当前跳跃表的层数
                self.level = rlevel

            # 生成新的节点
            n = Node(key, rlevel)

            # 插入每一层
            for i in range(rlevel + 1):
                n.forward[i] = update[i].forward[i]
                update[i].forward[i] = n

            self.size += 1
            # print("Successfully inserted key {}".format(key))

        
    def delete(self, search_key):
    
        update = [None] * (self.max_level + 1)
        current = self.header

        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < search_key:
                current = current.forward[i]
            update[i] = current

        current = current.forward[0]

        if current is not None and current.key == search_key:

            for i in range(self.level + 1):

                # 如果往上层没有要删除的节点则提前结束
                if update[i].forward[i] != current:
                    break
                update[i].forward[i] = current.forward[i]

            del current

            while self.level > 0 and self.header.forward[self.level] is None:
                self.level -= 1

            self.size -= 1
            print("Successfully deleted {}".format(search_key))

    def search(self, key):
        current = self.header
        n = 0
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
                n += 1
        print(n, "次")

        current = current.forward[0]

        if current and current.key == key:
            # print("Found key ", key)
            pass

    def printme(self):
        print("*****Skip List******")
        head = self.header
        for lvl in range(self.level + 1):
            print("Level {}: ".format(lvl))
            node = head.forward[lvl]
            node_list = []
            while node is not None:
                node_list.append(str(node.key))
                node = node.forward[lvl]
            print("->".join(node_list))


if __name__ == "__main__":
    # Simple test
    # TODO: This should be put in a test suite.
    from random import randint
    seed(8)
    l = [randint(0, 900) for x in range(800)]
    seed(31)
    print('Running skiplist test:')
    mylist = SkipList(expected_size=800, p=0.25)
    for x in l:
        mylist.insert(x)

    print('Initial list:')
    print('Size: ', mylist.size)
    mylist.printme()
    # delete some keys
    d = [randint(0, 900) for x in range(200)]
    # d = [510, 507]
    for x in d:
        print('Deleteing key: ', x)
        mylist.delete(x)

    # After delete：
    print(f'Size: {mylist.size}')
    print('Done')