

"""
假设一个二叉搜索树具有如下特征：

节点的左子树只包含小于当前节点的数。
节点的右子树只包含大于当前节点的数。
***所有左子树和右子树自身必须也是二叉搜索树***

"""


class BinarySearchNode():
    def __init__(self, k, v):
        self.key = k
        self.val = v
        self.left = None
        self.attach = set() # hashSet附加值
        self.right = None

    
class BInarySearchTree:
    def __init__(self):
        pass
    
    def add(self, key, val, tree: BinarySearchNode):
        if tree is None:
            return BinarySearchNode(key, val)
        
        # 右字树
        if key > tree.key:
            tree.right = self.add(key, val, tree.right)
        # 左字树
        if key < tree.key:
            tree.left = self.add(key, val, tree.left)

        # 将val追加到附加值，或者对应重复元素
        if key == tree.key:
            tree.attach.add(val)

        return tree

    def searchRange(self, s, e, res: list, tree: BinarySearchNode):
        """范围查询
        : b begin
        : e end
        : 查询的tree
        """
        
        if tree is None:
            return res
        
        # 左子树 (寻找下界)
        if s < tree.key:
            self.searchRange(s, e, res, tree.left)

        # 当前节点是否在选定范围内
        if s <= tree.key and e >= tree.key:
            for item in tree.attach:
                res.append(item)
            
        # 遍历右子树(1： 找到s(min)的下限, 2: 必须在e(Max)范围呢)
        if s > tree.key or e > tree.key:
            self.searchRange(s, e, res, tree.right)
        
        return res

    def remove(self, key, val, tree: BinarySearchNode):
        if tree is None:
            return None
        
        # 左子树
        if key < tree.key:
            tree.left = self.remove(key, val, tree.left)
        # 右子树
        if key > tree.key:
            tree.right = self.remove(key, val, tree.right)

        # 相等的情况
        if key == tree.key:
            # 判断hashset中是否有多个值
            if tree.attach.count > 1:
                tree.attach.remove(val)
            else:
                # 分为两种情况
                # 有两个孩子的情况，找直接前驱或者直接后继
                if tree.left != None and tree.rigth != None:
                    # 直接后继(右子树的最左节点)
                    node = self.findMinNode(tree.right)
                    tree.key = node.key
                    tree.val = node.val
                    tree.attach = node.attach
                    # 直接前驱(左字树的最右节点)
                    # tree.key = self.findMaxNode(tree.left).key
                    # 删除该直接后继节点
                    tree.right = self.remove(tree.key, val, tree.right)
                else:
                    tree = tree.right if tree.left is None else tree.left

        return tree

    def search(self, key, tree: BinarySearchNode):
        if tree is None or tree.key == key:
            return tree
        if key < tree.key:
            return self.search(tree.left, key)
        if key > tree.key:
            return self.search(tree.right, key)
        return tree.attach.pop()
    
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