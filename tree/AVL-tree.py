"""
平衡二叉树(AVL)
平衡二叉树 （Height-Balanced Binary Search Tree） 是一种二叉排序树，
其中**每一个结点的左子树和右子树的高度差不超过1（小于等于1）**

二叉树的平衡因子 （Balance Factor） 等于该结点的左子树深度减去右子树深度的值称为平衡因子。平衡因子只可能是－1，0，1。
距离插入结点最近的，且平衡因子的绝对值大于1的结点为根的子树，称为最小不平衡子树

平衡二叉树就是二叉树的构建过程中，每当插入一个结点，看是不是因为树的插入破坏了树的平衡性，
若是，则找出最小不平衡树。在保持二叉树特性的前提下，调整最小不平衡子树中各个结点之间的链接关系，
进行相应的旋转，使之成为新的平衡子树。简记为： 步步调整，步步平衡 
"""


class AVLNode():
    def __init__(self, k, v):
        self.key = k
        self.val = v
        self.height = 0  # 高度
        self.attach = () # 附加值
        self.left = None
        self.right = None


class AVLTree():
    def __init__(self):
        pass

    def rotateAtLL(self, node: AVLNode):
        """
        右旋
        """
        # 左左情况 （左子树的左边节点）
        top = node.left
        # 先截断当前节点的左孩子
        node.left = top.right
        # 把当前节点作为temp的右孩子
        top.right = node
        # 重新计算两个节点的高度
        node.height = self.maxDepth(node)
        top.height = self.maxDepth(top)

        return top

    def rotateAtRR(self, node: AVLNode):
        # 左旋
        # 右右情况，右子树的右边节点多了，导致失衡
        top = node.right    
        node.right = top.left
        top.left = node

        node.height = self.maxDepth(node)
        top.height = self.maxDepth(top)
        
        return top

    def rotateLR(self, node: AVLNode):
        # 左右情况，左子树的右边节点失衡
        # 先进行左旋，此时变成左左的情况
        node.left = self.rotateAtRR(node.left)
        # 在进行右旋
        return self.rotateAtLL(node)

    def rotateRL(self, node: AVLNode):
        # 右左双旋转的情况（右子树的左边节点）
        # 先进行右旋.
        node.right = self.rotateAtLL(node.right)
        # 在进行左旋
        return self.rotateAtRR(node)

    def add(self, key, value, tree: AVLNode):
        if tree == None:
            return AVLNode(key, value)
        
        # 左子树
        if key < tree.key:
            # 递归比较左子树
            tree.left = self.add(key, value, tree.left)

            if self.curNodeHeight(tree.left) - self.curNodeHeight(tree.right) == 2:
                # 说明此时是左左情况，要对最小不平衡子树做右旋
                if key < tree.left.key:
                    tree = self.rotateAtLL(tree.left)
                else:
                    # 属于左右情况, 要做左平衡操作
                    tree = self.rotateLR(tree.left)
        # 走右子树
        if key > tree.key:
            tree.right = self.add(key, value, tree.right)
            if self.curNodeHeight(tree.right) - self.curNodeHeight(tree.left) == 2:
                # 此时是右右情况, 要对最小不平衡子树做左旋
                if key > tree.right.key:
                    tree = self.rotateAtRR(tree.right)
                else:
                    # 属于右左旋转, 要做左平衡操作
                    tree = self.rotateRL(tree.right)

        # 将value 追加到附加值中
        if key == tree.key:
            tree.attach.add(value)
        
        # 重新计算高度1
        tree.height = self.maxDepth(tree)

        return tree
 
    def remove(self, key, val, tree: AVLNode):
        if tree == None:
            return AVLNode(key, val)
        
        # 左字树
        if key < tree.key:
            tree.left = self.remove(key, val, tree.left)
            # 如果说相差等于2就说明这棵树要旋转了
            if self.curNodeHeight(tree.left) - self.curNodeHeight(tree.right) == 2:
                # 说明此时是左左旋转
                if key < tree.left.right:
                    tree = self.rotateAtLL(tree.left)
                else:
                    # 属于左右旋转
                    tree = self.rotateLR(tree.left)
        # 右子树
        if key > tree.key:
            tree.right = self.remove(key, val, tree.right)
            if self.curNodeHeight(tree.right) - self.curNodeHeight(tree.left) == 2:
                # 此时是右右旋转
                if key > tree.right.key:
                    tree = self.rotateAtRR(tree.right)
                else:
                    tree = self.rotateRL(tree.right)

        # 相等的情况
        if key == tree.key:
            # 判断hashset中是否有多值
            if tree.attach.Count() > 1:
                # 实现惰性删除
                tree.attach.remove(val)
            else:
                # 有两个子孩子的情况
                if tree.left != None and tree.right != None:
                    # 根据平衡二叉树的中序遍历找到后继节点(需要找到有字数的最小节点)
                    # 直接后继(右子树的最左节点)
                    node = self.findMinNodeRecur(tree.right)
                    tree.key = node.key
                    tree.val = node.val
                    tree.attach = node.attach
                    # 删除右子树的指定元素
                    tree.right = self.remove(tree.key, val, tree.right)
                else:
                    # 自减高度
                    tree = tree.right if tree.left == None else tree.left

                    # 如果删除的是叶子节点则直接返回
                    if tree == None:
                        return None            
        
        tree.height = self.maxDepth(tree)

        return tree
    
    def findMin(self):
        pass

    def curNodeHeight(self, node: AVLNode):
        return -1 if node is None else node.height

    def maxDepth(self, node: AVLNode):
            # # 后序遍历计算树的深度
        return max(self.curNodeHeight(node.left), self.curNodeHeight(node.right)) + 1
    
    @staticmethod
    def findMinNode(tree):
        # 最左节点
        if tree is None:
            return None
        while tree.left is not None:
            tree = tree.left
        return tree

    def findMinNodeRecur(self, tree):
        if tree is None or tree.left is None:
            return None
        return self.findMinNodeRecur(tree.left)

    @staticmethod
    def findMaxNode(tree):
        # 最右节点
        if tree is None:
            return None
        while tree.right is not None:
            tree = tree.right
        return tree

    def findMaxNodeRecur(self, tree):
        if tree is None or tree.right is None:
            return tree
        return self.findMaxNodeRecur(tree.right)
