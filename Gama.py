# -*- coding: utf-8 -*-
# @Time    : 2018/11/5 下午 06:22
# @Author  : AlexJean
import numpy as np
from enum import Enum


class GamaCode:
    """
    要制作的TrainData output
    改為 每個點一個Vector, 強度為梯度, 方向0...7
    暫不處理SuperResolution, 能力不足
    """
    Black = 1
    White = 2
    NotEdge = 0

    def __init__(self, w, h):
        self.marked = np.zeros((w, h), np.uint8)
        self.Wid = w
        self.Hei = h

    def getEdgeList(self, data):
        da = (np.array(data) > 127)  # 把 0- 127 黑False   128-254白 True
        for x in range(1, self.Wid):
            if x % 10 == 0:
                print(self.Wid - x, end=' ', flush=True)
                if x % 100 == 0:
                    print(' ')
            for y in range(1, self.Hei):
                if self.marked[x, y] == GamaCode.NotEdge:
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
        print('  end of getEdgeList')
        return

    def markEdge(self, c, x, y):
        if c:
            self.marked[x, y] = GamaCode.White
        else:
            self.marked[x, y] = GamaCode.Black

    def checkEdge(self, me, other, x, y):
        if me == other:  # 二點同色
            return False
        if self.marked[x, y] != GamaCode.NotEdge:  # 己被標記是edge
            return False
        self.markEdge(other, x, y)

    def valueEdge(self, x, y):
        white, black = 0, 0
        for x1 in range(x, x+4):
            for y1 in range(y, y+4):
                c = self.marked[x1, y1]
                if c == GamaCode.NotEdge:
                    continue
                elif c == GamaCode.White:
                    white += 1
                elif c == GamaCode.Black:
                    black += 1
        if white > black:
            return white + black * 2
        return black + white * 2


