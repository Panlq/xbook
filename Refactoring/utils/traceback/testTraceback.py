#!usr/bin/python3
# -*- coding:utf-8 -*-

import sys
import traceback
import logging


logger = logging.getLogger('traceback_test')


def func1():
    raise NameError('---func exception---')


def func2():
    func1()


def main():
    try:
        func2()
    except Exception as e:
        exc_type, exc_value, exc_traceback_obj = sys.exc_info()
        # print(f'exc_type: {exc_type}')
        # print(f'exc_value: {exc_value}')
        # print(f'exc_traceback_obj: {exc_traceback_obj}')

        # 
        # traceback.print_tb(exc_traceback_obj, limit=1)
        # traceback.print_exception(exc_type, exc_value, exc_traceback_obj, limit=1, file=sys.stdout, chain=True)
        # traceback.print_exc()
        # traceback.print_exc(limit=1)
        # traceback.print_exc(limit=1, file=sys.stdout)

        # traceback.format_exc 会返回错误信息字符串 一般结合logger 使用
        # exc_info = traceback.format_exc()
        # print(exc_info)
        logger.error(traceback.format_exc(limit=1))


if __name__ == '__main__':
    main()
