# -*- coding: utf-8 -*-
# @Time    : 2018/11/5 下午 06:22
# @Author  : AlexJean
import numpy as np
from enum import Enum


class GaCo:
    """
    要制作的TrainData output
    改為 每個點一個 強度 (梯度?)  offset ( 0> 1\ 2V 3/ ) <= stride2 shift
    鄰居8點加自己投票定,本'井字'最sharp offset. 但offset只用於本點
    暫不處理SuperResolution, 能力不足
    """
    Black = 1
    White = 2
    NotEdge = 0
    Dir9 = [[0, 0], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]]
    Dir8 = [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]]

    def __init__(self, w, h):
        self.marked = np.zeros((w, h), np.uint8)
        self.Wid = w
        self.Hei = h
        # below variables  for evaluateStride2Map
        self.W2 = w // 2 - 1
        self.H2 = h // 2 - 1
        stride2dim = (self.W2, self.H2)
        self.stride2 = np.zeros(stride2dim, np.int16)
        self.worldData = None
        self.contrastData = np.zeros(stride2dim, np.int32)
        self.forbidLevel = np.zeros(stride2dim, np.int32)
        self.forbidBy = np.zeros(stride2dim, np.object)

    def getEdgePoint(self, data):
        print('Begin getEdgeList =====================')
        da = (np.array(data) > 127)  # 把 0- 127 黑False   128-254白 True
        for x in range(1, self.Wid):
            if x % 10 == 0:
                print(x, end=' ', flush=True)
                if x % 100 == 0:
                    print(' ')
            for y in range(1, self.Hei):
                if self.marked[x, y] == GaCo.NotEdge:
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
            self.marked[x, y] = GaCo.White
        else:
            self.marked[x, y] = GaCo.Black

    def checkEdge(self, me, other, x, y):
        if me == other:  # 二點同色
            return False
        if self.marked[x, y] != GaCo.NotEdge:  # 己被標記是edge
            return False
        self.markEdge(other, x, y)

    def valueEdge(self, x, y):
        white, black = 0, 0
        for x1 in range(x, x + 4):
            for y1 in range(y, y + 4):
                c = self.marked[x1, y1]
                if c == GaCo.NotEdge:
                    continue
                elif c == GaCo.White:
                    white += 1
                elif c == GaCo.Black:
                    black += 1
        if white > black:
            return white + black * 2
        return black + white * 2

    def evaluateDiv4Map(self, data):
        print("Begin valueDive4Map　============")
        w, h = self.Wid // 4, self.Hei // 4
        for x in range(w):
            if x % 20 == 0:
                print(x, end=' ', flush=True)
            for y in range(h):
                data[x, y] = self.valueEdge(x * 4, y * 4) * 10
        print("\ncompleted!")

    def evaluateStride2Map(self):
        print("Begin valueStride2Map "+'='*51)
        w2, h2 = self.W2, self.H2
        for x in range(0, w2):
            if x % 20 == 0:
                print(x, end=' ', flush=True)
            for y in range(0, h2):
                self.stride2[x, y] = self.valueEdge(x * 2, y * 2)  # 這個值拿來算Variance的,先不乘10
        print("\ncompleted!")

    def evaluateAllContrast(self):
        print("Begin valueAllContrast " + '=' * 123)
        w2, h2 = self.W2, self.H2
        for x in range(2, w2-2):
            if x % 10 == 0:
                print(x, end=' ', flush=True)
            for y in range(2, h2-2):
                self.contrastData[x, y] = self.contrast(x, y)
        print("\ncompleted!")

    def markFullForbidden(self, x, y, forbidLevel):
        relist = []
        pos = (x, y)
        for di in GaCo.Dir8:
            x2, y2 = x + di[0], y + di[1]
            level = self.forbidLevel[x2, y2]
            if level == 0:
                self.forbidBy[x2, y2] = pos
                self.forbidLevel[x2, y2] = -forbidLevel
            elif level > 0:                     # 有人佔位
                if level > forbidLevel:         # 人家強 , 外面有檢查最強才進來,應該不可能
                    print("Err1({},{})".format(x, y))
                else:                           # 我們強, 他重定位
                    x3, y3 = self.forbidBy[x2, y2]
                    self.clearPosition(x3, y3)
                    relist.append((x3, y3))
            elif (-level) > forbidLevel:        # 別人禁區較強 ^^" 繞開
                pass
            else:
                self.forbidBy[x2, y2] = pos     # 我們強, 改我們禁區
                self.forbidLevel[x2, y2] = -forbidLevel
        self.forbidLevel[x, y] = forbidLevel
        self.forbidBy[x, y] = pos
        for (x, y) in relist:
            self.rePosition(x, y)
        return list

    def clearForbidden(self, x, y):
        pos = (x, y)
        for di in GaCo.Dir8:
            x1, y1 = x+di[0], y+di[1]
            if self.forbidBy[x1, y1] == pos:
                self.forbidLevel[x1, y1] = 0
                self.forbidBy[x1, y1] = 0
        self.forbidLevel[x, y] = 0
        self.forbidBy[x, y] = 0

    def setWorldData(self, x, y):
        self.worldData[x, y] = self.stride2[x, y] * 10

    def clearPosition(self, x, y):
        self.worldData[x, y] = 0
        self.clearForbidden(x, y)

    def rePosition(self, x, y):
        x -= (x % 2)
        y -= (y % 2)
        x4, y4, var4 = self.maxContrastPartial(x, y)
        if var4 > 0:                                                        # <=0 無路可走
            self.markForbidden(x4, y4, var4)
            self.setWorldData(x4, y4)

    def markForbidden(self, x, y, forbidLevel):                             # 用於rePosition內部, 不處理relist
        pos = (x, y)
        for di in GaCo.Dir8:
            x2, y2 = x + di[0], y + di[1]
            level = self.forbidLevel[x2, y2]
            if level == 0:
                self.forbidBy[x2, y2] = pos
                self.forbidLevel[x2, y2] = -forbidLevel
            elif level > 0:                     # 有人佔位
                if level > forbidLevel:         # 人家強 , 外面有檢查最強才進來,應該不可能
                    print("Err2({},{})".format(x, y))
                else:                           # 我們強, 清除他,不relist,以免recursive
                    x3, y3 = self.forbidBy[x2, y2]
                    self.clearPosition(x3, y3)
            elif (-level) > forbidLevel:        # 別人禁區較強 ^^" 繞開
                pass
            else:
                self.forbidBy[x2, y2] = pos     # 我們強, 改我們禁區
                self.forbidLevel[x2, y2] = -forbidLevel
        self.forbidLevel[x, y] = forbidLevel
        self.forbidBy[x, y] = pos

    def evaluateSmartDiv4Map(self, stride2world):
        self.evaluateStride2Map()      # data put in self.stride2
        self.evaluateAllContrast()
        print("Begin fill stride2world "+'='*42)
        w, h = self.Wid // 4, self.Hei // 4
        self.worldData = stride2world.Data
        for x in range(2, w-2):
            if x % 10 == 0:
                print(x, end=' ', flush=True)
            for y in range(2, h-2):
                x1, y1 = x * 2, y * 2
                x2, y2, var = self.maxContrastAll(x1, y1)
                if var <= 0:
                    continue
                level = self.forbidLevel[x2, y2]
                if level == 0:                                        # 此點無禁制
                    self.markFullForbidden(x2, y2, var)
                elif level > 0 or (-level) >= var:                    # 鄰居本尊, 佔同一位置Contrast必相同, 故讓
                    x2, y2, var = self.maxContrastPartial(x1, y1)     # or 鄰居禁區, 鄰居強 , 重定位
                    if var <= 0:                                      # 無路可走
                        continue
                    self.markFullForbidden(x2, y2, var)
                else:                                                 # else 鄰居禁區, 鄰居弱, 鄰居重算
                    x3, y3 = self.forbidBy[x2, y2]
                    self.clearPosition(x3, y3)
                    self.markFullForbidden(x2, y2, var)               # 此處或有第二鄰居,沖禁制
                    self.rePosition(x3, y3)
                self.setWorldData(x2, y2)
        print("\ncompleted!")
        stride2world.repaint()

    def maxContrastPartial(self, x1, y1):
        maxVar, mX, mY = -1, x1, y1
        for di in GaCo.Dir9:
            x, y = x1 + di[0], y1 + di[1]
            if self.forbidLevel[x, y] == 0:      # 負數代表己經被禁止了, 正數代表有點了
                var = self.contrastData[x, y]
                if var > maxVar:
                    maxVar, mX, mY = var, x, y
        return mX, mY, maxVar

    def maxContrastAll(self, x1, y1):
        maxVar, mX, mY = -1, x1, y1
        for di in GaCo.Dir9:
            x, y = x1 + di[0], y1 + di[1]
            var = self.contrastData[x, y]
            if var > maxVar:
                maxVar, mX, mY = var, x, y
        return mX, mY, maxVar

    # x,y 算二次, 加其他8方向,湊成10
    def contrast(self, x, y):
        v = self.stride2
        direction = [[2, 0], [2, 2], [0, 2], [-2, 2], [-2, 0], [-2, -2], [0, -2], [2, -2]]
        u = v[x, y] * 2
        for di in direction:
            u += v[x + di[0], y + di[1]]
        var = GaCo.variance(v[x, y] * 10, u) * 2
        for di in direction:
            var += GaCo.variance(v[x+di[0], y + di[1]] * 10, u)
        return var

    # int pow2
    @staticmethod
    def variance(val, u):
        z = val - u
        return z * z
