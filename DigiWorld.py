# -*- coding: utf-8 -*-
# @Time    : 2018/8/20 下午 06:37
# @Author  : AlexJean
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from World import World


class EdgeWorld(World):
    def __init__(self, viewEdge, w, h, dat):
        super().__init__(viewEdge, w * 4, h * 4, None)
        self.sourceData = dat
        self.sourceWidth = w
        self.sourceHeight = h
        self.Edge = np.zeros([w, h, 2], bool)

    @staticmethod
    def abs4Uint(a, b):
        if a >= b:
            return a - b
        return b - a

    def markEdge(self):
        for i in range(0, self.sourceWidth - 1):
            for j in range(0, self.sourceHeight - 1):
                c = self.sourceData[i, j]
                self.Edge[i, j, 0] = (EdgeWorld.abs4Uint(c, self.sourceData[i, j + 1]) > 50)  # downEdge  放在 0
                self.Edge[i, j, 1] = (EdgeWorld.abs4Uint(c, self.sourceData[i + 1, j]) > 50)  # rightEdge 放在 1

    def drawScreen(self, qp):
        for i in range(self.sourceWidth):
            for j in range(self.sourceHeight):
                qp.setPen(Qt.black)
                i1 = i * 4
                j1 = j * 4
                for x in range(4):
                    for y in range(4):
                        qp.drawPoint(x + i1, y + j1)
                if self.Edge[i, j, 0]:
                    qp.setPen(Qt.white)
                    for x in range(4):
                        qp.drawPoint(x + i1, 3 + j1)
                if self.Edge[i, j, 1]:
                    qp.setPen(Qt.white)
                    for y in range(4):
                        qp.drawPoint(3 + i1, y + j1)


class Shrink(World):
    def __init__(self, view, w, h, data):
        super().__init__(view, w, h, data)

    def drawScreen(self, qp):
        for i in range(0, self.Width - 1, 2):
            for j in range(0, self.Height - 1, 2):
                c = 0
                c += self.Data[i, j]
                c += self.Data[i + 1, j]
                c += self.Data[i, j + 1]
                c += self.Data[i + 1, j + 1]
                c /= 4
                qp.setPen(QColor(c, c, c))
                qp.drawPoint(i, j)
                qp.drawPoint(i + 1, j)
                qp.drawPoint(i, j + 1)
                qp.drawPoint(i + 1, j + 1)


class DigiWorld(World):
    def __init__(self, view, view1, viewEdge, w, h):
        super().__init__(view, w, h)
        self.ShrinkWorld = Shrink(view1, w, h, self.Data)
        self.edgeWorld = EdgeWorld(viewEdge, w, h, self.Data)
        print("Width%s Height%s world%s created!" % (self.Width, self.Height, self))

    def before_repaint(self):
        self.edgeWorld.markEdge()

    def repaint(self):
        super().repaint()
        self.ShrinkWorld.repaint()
        self.edgeWorld.repaint()

    def clearWorld(self):
        self.Data[:] = 0
        self.before_repaint()
        self.repaint()
