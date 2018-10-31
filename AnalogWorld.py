# -*- coding: utf-8 -*-
# @Time    : 2018/9/7 下午 05:42
# @Author  : AlexJean

import numpy as np
from World import World
from Alpha import AlphaCode
import Beta


class Div4World(World):
    def __init__(self, view, w, h):
        super().__init__(view, w, h)
        self.trainLabel = np.zeros([w, h], np.int16)


class AnalogWorld(World):
    def __init__(self, view, viewLarge, w, h):
        super().__init__(viewLarge, w * 4, h * 4)
        self.div4World = Div4World(view, w, h)
        print("Width%s Height%s world%s created!" % (self.Width, self.Height, self))

    @staticmethod
    def isAlphaEdge(direction, me, other):
        if me == other:
            return False
        if me == AlphaCode.BlackPlate and other == AlphaCode.WhitePlate:
            return True
        elif me == AlphaCode.WhitePlate and other == AlphaCode.BlackPlate:
            return True
        # 不是連接色, 要移半格精度計算
        return False

    def calcAlphaLabel(self):
        w = self.div4World.Width
        h = self.div4World.Height
        print("計算一刀切 全黑或全白", end=' ', flush=True)
        tempLabel = np.zeros([w, h], np.int16)
        for x in range(w):
            if x % 10 == 0:
                print(w - x, end=' ', flush=True)
            for y in range(h):
                x1, y1 = x * 4, y * 4
                tempLabel[x, y] = AlphaCode.Estimate(self.Data[x1:x1 + 4, y1:y1 + 4])
        # 計算半格的
        print("\n移位半格計算'正邊線'", end=' ', flush=True)
        DirUp = 0x1000
        DirDown = 0x0100
        DirLeft = 0x0010
        DirRight = 0x0001
        for x in range(1, w - 1):
            if x % 10 == 0:
                print(w - x, end=' ', flush=True)
            for y in range(1, h - 1):
                c = tempLabel[x, y]
                if (c != AlphaCode.BlackPlate) and (c != AlphaCode.WhitePlate):  # 只處理黑白, 一刀切的不管
                    self.div4World.trainLabel[x, y] = c
                else:
                    code = 0
                    up = tempLabel[x, y - 1]
                    down = tempLabel[x, y + 1]
                    left = tempLabel[x - 1, y]
                    right = tempLabel[x + 1, y]
                    if self.isAlphaEdge(DirUp, c, up):
                        code |= DirUp
                    if self.isAlphaEdge(DirDown, c, down):
                        code |= DirDown
                    if self.isAlphaEdge(DirLeft, c, left):
                        code |= DirLeft
                    if self.isAlphaEdge(DirRight, c, right):
                        code |= DirRight
                    if code == 0:
                        self.div4World.trainLabel[x, y] = c
                    else:
                        self.div4World.trainLabel[x, y] = (code << 8) & c
        print("\ncalcTrainLabel successed!\n")

    def calcBetaLabel(self):
        w, h = self.div4World.Width, self.div4World.Height
        w2, h2 = w * 2, h * 2
        evaluate = np.zeros([w2, h2], np.int16)
        for x in range(w2 - 1):
            if x % 10 == 0:
                print(w2 - x, end=' ', flush=True)
            for y in range(h2 - 1):
                beta = Beta.BetaCode()
                x2, y2 = x * 2, y * 2
                score = beta.Estimate(self.Data[x2:x2 + 4, y2:y2 + 4])
                evaluate[x, y] = score
        print("\ncalcBetaLabel successed!\n")
        for i in range(self.Width):
            for j in range(self.Height):
                if self.Data[i, j] > 40:
                    self.Data[i, j] = 40
        for x in range(w2):
            for y in range(h2):
                if evaluate[x, y] > 3:
                    x2, y2 = x * 2, y * 2
                    self.Data[x2, y2] = 254
        self.repaint()

    def calcDiv4(self):
        w = self.div4World.Width
        h = self.div4World.Height
        small = self.div4World.Data
        for x in range(w):
            if x % 10 == 0:
                print(w - x, end=' ', flush=True)
            for y in range(h):
                x1 = x * 4
                y1 = y * 4
                s = np.sum(self.Data[x1:x1 + 4, y1:y1 + 4])
                small[x, y] = s / 16
        else:
            print("\ncalcDiv4 successed!\n")

    def before_repaint(self):
        self.calcDiv4()

    def repaint(self):
        super().repaint()
        self.div4World.repaint()

    #       self.edgeWorld.repaint()

    def clearWorld(self):
        self.Data[:] = 0
        self.before_repaint()
        self.repaint()
