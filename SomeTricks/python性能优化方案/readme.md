#### Python性能优化方案
1. 从编码方面入手，代码算法优化，如多重条件判断有限判断先决条件(可看 《改进python的91个建议》)
2. 使用Cython (核心算法, 对性能要求较大的建议使用Cython编写) 是python & c++的结合, 性能有数量级的提升
3. 使用ast抽象语法树 根据python CAPI扩展, 编写c++ python加载器 (即使用加载器将python 代码转为c++执行) 如开源模块 py2c

#### 记录笔记
**[python/C API Reference Manual ](https://docs.python.org/3.6/c-api/index.html)**

#### Cython 使用步骤
注: cython 编译环境，需要vc++14.0
需要安装visual studio 17以上版本  

1. 安装cython: pip install cython 
2. 编写.py或者.pyx文件 .pyx文件可用python语法和Cython语法建议使用Cython语法
3. 编译.pyx 文件为.pyd文件(二进制文件) 也是一种python代码加密方案
> python setup.py build_ext --inplace  # 编译命令


#### 文档记录
cython 中文文档: https://www.bookstack.cn/read/cython-doc-zh/README.md

> extension option 说明
- py_limited_api 使用受限API [官方说明](https://docs.python.org/zh-cn/3/c-api/stable.html)

#### 链接其他库或者文件

[官方说明参考](https://www.bookstack.cn/read/cython-doc-zh/docs-29.md)
```python
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

extension = [
    Extension(
        name='',
        sources='',
        include_dirs=[...],
        libraries=[...],
        library_dirs=[...]
    )
]

```