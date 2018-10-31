# -*- coding: utf-8 -*-
# @Time    : 2018/10/18 下午 06:42
# @Author  : AlexJean
import numpy as np


class BetaCode:
    def __init__(self):
        self.whiteCount, self.blackCount = 0, 0
        self.marked = np.zeros((4, 4), bool)
        pixelList = []

    # 找出黑白交界的Pixel
    def Estimate(self, data):
        if data.shape != (4, 4):
            raise Exception("Shape should be (4, 4)")
        da = (np.array(data) > 127)  # 把 0- 127 黑False   128-254白 True
        for x in range(1, 4):
            for y in range(1, 4):
                if not self.marked[x, y]:
                    x1, y1 = x - 1, y - 1
                    c, up, left = da[x, y], da[x, y1], da[x1, y]
                    if c != up or c != left:
                        self.markEdge(c, x, y)
                        self.checkEdge(c, up, x, y1)
                        self.checkEdge(c, left, x1, y)
        c, right, down = da[0, 0], da[1, 0], da[0, 1]
        if c != down or c != right:
            self.markEdge(c, 0, 0)
            self.checkEdge(c, down, 0, 1)
            self.checkEdge(c, right, 1, 0)
        evaluate = self.whiteCount + self.blackCount + min(self.whiteCount, self.blackCount)
        return evaluate

    def markEdge(self, c, x, y):
        self.marked[x, y] = True
        # 暫不算切線角度, pixelList先不用
        # self.pixelList.append((c, x, y))
        if c:
            self.whiteCount = self.whiteCount + 1
        else:
            self.blackCount = self.blackCount + 1

    def checkEdge(self, me, other, x, y):
        if me == other:  # 二點同色
            return False
        if self.marked[x, y]:  # 己被標記是edge
            return False
        self.markEdge(other, x, y)
