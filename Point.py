# -*- coding: utf-8 -*-
# @Time    : 2018/12/4 下午 03:51
# @Author  : AlexJean


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, obj):
        return Point(self.x + obj.x, self.y + obj.y)