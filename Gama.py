# -*- coding: utf-8 -*-
# @Time    : 2018/11/5 下午 06:22
# @Author  : AlexJean
import numpy as np
from Point import Point


class GameCode:
    """
    要制作的TrainData output
    改為 每個點一個Vector, 強度為梯度, 方向0...7
    暫不處理SuperResolution, 能力不足
    """
    def __init__(self, w, h):
        self.whiteList = []
        self.blackList = []
        self.marked = np.zeros((w, h), bool)

    def getEdgeList(self,data):
        return

    def countEdgeToDiv4World(self):
        return
