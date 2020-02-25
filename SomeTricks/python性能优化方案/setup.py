# 编译pyx文件为pyd文件

"""
python setup.py build --inplace

"""

import os, shutil
from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize
from functools import update_wrapper

__base_path = os.path.dirname(__file__)


def rmext(build_script, pyx_dir, pyx_name):
    shutil.rmtree(os.path.join(build_script, 'build'), ignore_errors=True)
    print('remove middleware build folder:', os.path.join(build_script, 'build'))
    c_path = os.path.join(pyx_dir, '%s.c' % (pyx_name))
    cpp_path = os.path.join(pyx_dir, '%s.cpp' % (pyx_name))

    if os.path.exists(c_path):
        os.remove(c_path)
        print('remove c_path:', c_path)

    if os.path.exists(cpp_path):
        os.remove(cpp_path)
        print('remove cpp_path:', cpp_path)
    

def compile_with_ext():
    import numpy
    extensions = [
        Extension(name='fb',
                py_limited_api=True,
                sources=['./version5.pyx'],
                include_dirs=[numpy.get_include()])
    ]
    setup(
        name='fb',
        ext_modules=cythonize(extensions)
    )

if __name__ == '__main__':
    # setup(ext_modules=cythonize('version4.pyx'))
    compile_with_ext()
    rmext(__base_path, './', 'version5')

