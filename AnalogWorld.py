# -*- coding: utf-8 -*-
# @Time    : 2018/9/7 下午 05:42
# @Author  : AlexJean

import numpy as np
from World import World
from Alpha import AlphaCode
import Beta
from Gama import GaCo


class LabeledWorld(World):
    def __init__(self, view, w, h):
        super().__init__(view, w, h, displayFactor=1)
        self.trainLabel = np.zeros([w, h], np.int16)

    def clearWorld(self):
        self.trainLabel[:, :] = 0
        super().clearWorld()


class AnalogWorld(World):
    def __init__(self, view, viewLarge, w, h, shrinkFactor, displayFactor):
        super().__init__(viewLarge, w * shrinkFactor, h * shrinkFactor, displayFactor=displayFactor)
        self.shrinkFactor = shrinkFactor
        self.displayFactor = displayFactor
        self.div4World = LabeledWorld(view, w, h)
        print("Width%s Height%s world%s created!" % (self.Width, self.Height, self))

    def calcGamaLabel(self, loadedWorld, stride2World):
        w, h = self.div4World.Width, self.div4World.Height
        gama = GaCo(w * self.shrinkFactor , h * self.shrinkFactor, shinkFactor=self.shrinkFactor)
        gama.getEdgePoint(self.Data)
        gama.evaluateDiv4Map(loadedWorld.Data)
        loadedWorld.repaint()
        gama.evaluateSmartDiv4Map(stride2World, self.div4World)

    def calcDiv4(self):
        w = self.div4World.Width
        h = self.div4World.Height
        small = self.div4World.Data
        f2 = self.shrinkFactor * self.shrinkFactor
        for x in range(w):
            if x % 10 == 0:
                print(w - x, end=' ', flush=True)
            for y in range(h):
                x1 = x * self.shrinkFactor
                y1 = y * self.shrinkFactor
                s = np.sum(self.Data[x1:x1 + self.shrinkFactor, y1:y1 + self.shrinkFactor])
                small[x, y] = s / f2
        else:
            print("\ncalcDiv4 successed!\n")

    def before_repaint(self):
        self.calcDiv4()

    def repaint(self):
        super().repaint()
        self.div4World.repaint()
    #       self.edgeWorld.repaint()

    def clearWorld(self):
        self.Data[:, :] = 0
        self.div4World.clearWorld()
        self.repaint()
