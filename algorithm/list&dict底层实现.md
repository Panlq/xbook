


#### python list 是一种采用分离式技术实现的动态(元素外置)顺序表
参看:[list底层扩容实现](http://soong.site/datastructure/index.html)


python 官方 list的扩容实现
```c++
    /* This over-allocates proportional to the list size, making room
     * for additional growth.  The over-allocation is mild, but is
     * enough to give linear-time amortized behavior over a long
     * sequence of appends() in the presence of a poorly-performing
     * system realloc().
     * The growth pattern is:  0, 4, 8, 16, 25, 35, 46, 58, 72, 88, ...
     */
    new_allocated = (newsize >> 3) + (newsize < 9 ? 3 : 6);
    
    /* check for integer overflow */
    if (new_allocated > PY_SIZE_MAX - newsize) {
        PyErr_NoMemory();
        return -1;
    } else {
        new_allocated += newsize;
    }
```

#### python 字典对象的实现原理
字典的底层是用hash表来存储key 和 value 的关系映射的。

哈希表（也叫散列表），根据关键值对(Key-value)而直接进行访问的数据结构。它通过把key和value映射到表中一个位置来访问记录，这种查询速度非常快，更新也快。而这个映射函数叫做哈希函数，存放值的数组叫做哈希表。 哈希函数的实现方式决定了哈希表的搜索效率。具体操作过程是：

- 数据添加：把key通过哈希函数转换成一个整型数字，然后就将该数字对数组长度进行取余，取余结果就当作数组的下标，将value存储在以该数字为下标的数组空间里。
- 数据查询：再次使用哈希函数将key转换为对应的数组下标，并定位到数组的位置获取value。 

但是，对key进行hash的时候，不同的key可能hash出来的结果是一样的，尤其是数据量增多的时候，这个问题叫做哈希冲突。python 用开放寻址法来解决冲突，如果余数有冲突的话，会利用checksum等其他校验方法来解决。

##### 开放寻址法
CPython使用伪随机探测(pseudo-random probing)的散列表(hash table)作为字典的底层数据结构。由于这个实现细节，只有可哈希的对象才能作为字典的键。字典的三个基本操作（添加元素，获取元素和删除元素）的平均事件复杂度为O(1)

>开放寻址法中，所有的元素都存放在散列表里，当产生哈希冲突时，通过一个探测函数计算出下一个候选位置，如果下一个获选位置还是有冲突，那么不断通过探测函数往下找，直到找个一个空槽来存放待插入元素。



参考:
流畅的python 第三章  
[python之禅](https://foofish.net/python_dict_implements.html)  
[Python字典底层实现原理](https://blog.csdn.net/answer3lin/article/details/84523332)
