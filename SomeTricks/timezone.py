# -*- coding:utf-8 -*-

# 时区感知的datetime对象

import pytz
import datetime


def utcnow():
    return datetime.datetime.now(tz=pytz.utc)


def isotime():
    return utcnow().isoformat()


## 可以使用iso8601模块解析包含ISO8601格式时间戳的字符串, 

import iso8601

# 时区感知的时间戳可以直接进行比较， 时区感知和非时区感知的时间戳不可直接进行比较
iso8601.parse_date(isotime) < utcnow()

