
## 
"""
递归遍历转换字典中的对象

递归规则:
1. 使用new 对象来存储递归变化值
2. 递归最小单元
"""


class Dict2Obj(dict):
    """ dot.notation access to dictionary attributes """
    def __init__(self, dict_):
        self.__dict__.update(dict_)



class Dotdict(dict):
    """ dot.notation access to dictionary attributes """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def interncode(raw_dict):
    data = {}

    def inner_list(array, aryObj):
        for item in array:
            if isinstance(item, dict):
                temp = {}
                inner_map(item, temp)
                aryObj.append(temp)
            elif isinstance(item, (list, tuple)):
                temp = []
                inner_list(item, temp)
                aryObj.append(temp)
            else:
                aryObj.append(item)

    def inner_map(dict_, dctObj):
        for k, val in dict_.items():
            if isinstance(val, dict):
                temp = {}
                inner_map(val, temp)
                dctObj[k] = Dotdict(temp)
            elif isinstance(val, (list, tuple)):
                temp = []
                inner_map(val, temp)
                dctObj[k] = temp
            else:
                dctObj[k] = val
    inner_map(raw_dict, data)
    return Dotdict(data)


def interncode2(dict_):
    def inner_recur(val):
        if isinstance(val, dict):
            val = Dotdict(val)
            for k, v in val.items():
                val[k] = inner_recur(v)
        elif isinstance(val, (list, tuple)):
            for i, v in enumerate(val):
                val[i] = inner_recur(v)

        return val

    for k, v in dict_.items():
        dict_[k] = inner_recur(v)
    
    return Dotdict(dict_)



if __name__ == '__main__':
    data = {'name': 'p', 'age': [1,2,{'ts': 12, 'pos': {'a': 12}}], 'val': {'time': 12, 'pos':1, 'b': {'cc': 'ststst'}}}
    res = interncode(data)
    res = interncode2(data)

    print(res)
    print(res.name)
    print(res.val.time)
    print(res.val.b.cc)