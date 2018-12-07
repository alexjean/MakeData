# -*- coding: utf-8 -*-
# @Time    : 2018/9/7 下午 05:42
# @Author  : AlexJean

import numpy as np
from World import World
from Alpha import AlphaCode
import Beta
from Gama import GamaCode


class Div4World(World):
    def __init__(self, view, w, h):
        super().__init__(view, w, h)
        self.trainLabel = np.zeros([w, h], np.int16)


class AnalogWorld(World):
    def __init__(self, view, viewLarge, w, h):
        super().__init__(viewLarge, w * 4, h * 4)
        self.div4World = Div4World(view, w, h)
        print("Width%s Height%s world%s created!" % (self.Width, self.Height, self))

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
                    if AlphaCode.isEdge(DirUp, c, up):
                        code |= DirUp
                    if AlphaCode.isEdge(DirDown, c, down):
                        code |= DirDown
                    if AlphaCode.isEdge(DirLeft, c, left):
                        code |= DirLeft
                    if AlphaCode.isEdge(DirRight, c, right):
                        code |= DirRight
                    if code == 0:
                        self.div4World.trainLabel[x, y] = c
                    else:
                        self.div4World.trainLabel[x, y] = (code << 8) & c
        print("\ncalcTrainLabel successed!\n")

    def calcBetaLabel(self):
        w, h = self.div4World.Width, self.div4World.Height
        w2, h2 = w * 2, h * 2
        val = np.zeros([w2, h2], np.int16)
        for x in range(w2 - 1):
            if x % 10 == 0:
                print(w2 - x, end=' ', flush=True)
            for y in range(h2 - 1):
                beta = Beta.BetaCode()
                x2, y2 = x * 2, y * 2
                val[x, y] = beta.Estimate(self.Data[x2:x2 + 4, y2:y2 + 4])
        print("\ncalcBetaLabel successed!\n")
        for i in range(self.Width):
            for j in range(self.Height):
                if self.Data[i, j] > 40:
                    self.Data[i, j] = 40
        val1 = np.zeros((w2, h2), np.int16)
        # 取4格的Max
        '''
        for x in range(w2-1):
            for y in range(h2-1):
                if val[x, y] > val[x, y+1]:
                    x1, y1 = x, y
                else:
                    x1, y1 = x, y+1
                if val[x+1, y] > val[x+1, y+1]:
                    x2, y2 = x+1, y
                else:
                    x2, y2 = x+1, y + 1
                if val[x1, y1] > val[x2, y2]:
                    if val[x1, y1] > 4:
                        val1[x1, y1] = val[x1, y1]
                else:
                    if val[x2, y2] > 4:
                        val1[x2, y2] = val[x2, y2]
        '''
        for x in range(w2):
            for y in range(h2):
                if val[x, y]:
                    self.Data[x * 2, y * 2] = 254
        self.repaint()

    def calcGamaLabel(self, world):
        w, h = self.div4World.Width, self.div4World.Height
        gama = GamaCode(w * 4, h * 4)
        gama.getEdgePoint(self.Data)
        gama.valueDiv4Map(world.Data)
        world.repaint()
        gama.valueStride2Map()



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
