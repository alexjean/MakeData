# -*- coding: utf-8 -*-
# @Time    : 2018/11/5 下午 06:22
# @Author  : AlexJean
import numpy as np
from enum import Enum


class GamaCode:
    """
    要制作的TrainData output
    改為 每個點一個 強度 (梯度?)  offset ( 0> 1\ 2V 3/ ) <= stride2 shift
    鄰居8點加自己投票定,本'井字'最sharp offset. 但offset只用於本點
    暫不處理SuperResolution, 能力不足
    """
    Black = 1
    White = 2
    NotEdge = 0

    def __init__(self, w, h):
        self.marked = np.zeros((w, h), np.uint8)
        self.Wid = w
        self.Hei = h
        self.W2 = w // 2 - 1
        self.H2 = h // 2 - 1
        self.stride2 = np.zeros((self.W2, self.H2), np.int16)

    def getEdgePoint(self, data):
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
        print('\nend of getEdgeList')
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

    def valueDiv4Map(self, data):
        w, h = self.Wid // 4, self.Hei // 4
        for x in range(w):
            if x % 20 == 0:
                print(w - x, end=' ', flush=True)
            for y in range(h):
                data[x, y] = self.valueEdge(x * 4, y * 4) * 10
        print("\nvalueDive4Map　completed!")

    def valueStride2Map(self):
        w2, h2 = self.W2, self.H2
        for x in range(0, w2, 2):
            if x % 20 == 0:
                print(w2 - x, end=' ', flush=True)
            for y in range(0, h2, 2):
                self.stride2[x, y] = self.valueEdge(x * 2, y * 2) * 10
        print("\nvalueStride2Map　completed!")





