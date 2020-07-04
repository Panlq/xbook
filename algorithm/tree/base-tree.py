#!/usr/bin/python3
# -*- coding: utf-8 -*-
# __author__ = '__JonPan__'


from collections import deque

class Node(object):
    def __init__(self, elem=-1, lchild=None, rchild=None):
        self.elem = elem
        self.lchild = lchild
        self.rchild = rchild


class Tree(object):
    def __init__(self, root=None):
        self.root = root

    def add(self, elem):
        node = Node(elem)
        if self.root == None:
            self.root = node
        else:
            queue = deque()
            queue.append(self.root)
            while queue:
                cur = queue.popleft()
                if cur.lchild == None:
                    cur.lchild = node
                    return 
                elif cur.rchild == None:
                    cur.rchild = node
                else:
                    #如果左右子树都不为空，加入队列继续判断下一层级
                    queue.append(cur.lchild)
                    queue.append(cur.rchild)


    def preorder(self, root):
        # 先序遍历  根节点->左子树->右子树
        if root == None:
            return
        print(root.elem)
        self.preorder(root.lchild)
        self.preorder(root.rchild)

    def inorder(self, root): 
        # 递归实现中序遍历 左子树->根节点->右子树
        if root == None:
            return 
        self.inorder(root.lchild)
        print(root.elem)
        self.inorder(root.rchild)

    def postorder(self, root):
        # 递归实现后序遍历  左子树->右子树->根节点
        if root == None:
            return 
        self.postorder(root.lchild)
        self.postorder(root.rchild)
        print(root.elem)

    def breadth_travel(self):
        """利用队列实现树的层次遍历"""
        if root == None:
            return 
        queue = deque()
        queue.append(root)
        while queue:
            node = queue.popleft()
            print(node.elem)
            if node.lchild != None:
                queue.append(node.lchild)
            if node.rchild != None:
                queue.append(node.rchild)