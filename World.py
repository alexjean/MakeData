# -*- coding: utf-8 -*-
# @Time    : 2018/9/7 下午 02:02
# @Author  : AlexJean
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from Point import Point


class World(QWidget):
    def __init__(self, view, w, h, data=None):
        super().__init__(view, Qt.Widget)
        self.Width = w
        self.Height = h
        if data is None:
            self.Data = np.zeros([w, h], np.int32)
        else:
            self.Data = data
        self.resize(w, h)
        self.move(2, 2)

    def paintEvent(self, paintEvent):
        qp = QPainter()
        qp.begin(self)
        self.drawScreen(qp)
        qp.end()

    def drawScreen(self, qp):
        blank = QColor(0, 0, 0)
        for x in range(self.Width):
            for y in range(self.Height):
                c = self.Data[x, y]
                if c <= 0:
                    qp.setPen(blank)
                else:
                    qp.setPen(QColor(c, c, c))
                qp.drawPoint(x, y)

    def drawLine(self, p1, p2):
        if p1.x == p2.x:
            x1 = p1.x
            if (x1 < 0) or (x1 >= self.Width):
                return
            if p1.y > p2.y:
                begin, end = p2, p1
            else:
                begin, end = p1, p2
            if (begin.y >= self.Height) or (end.y < 0):
                return
            # print("Line(%s,%s) (%s,%s) created!" % (begin.x, begin.y, end.x, end.y))
            if begin.y < 0:
                begin.y = 0
            if end.y > self.Height:
                end.y = self.Height
            for y1 in range(begin.y, end.y, 1):
                self.Data[x1, y1] = 254  # 暫時保留255, 做特別標記
            return
        elif p1.y == p2.y:
            y1 = p1.y
            if (y1 < 0) or (y1 >= self.Height):
                return
            if p1.x > p2.x:
                begin, end = p2, p1
            else:
                begin, end = p1, p2
            if (begin.x >= self.Width) or (end.x < 0):
                return
            if begin.x < 0:
                begin.x = 0
            if end.x > self.Width:
                end.x = self.Width
            for x1 in range(begin.x, end.x, 1):
                self.Data[x1, y1] = 254  # 暫時保留255, 做特別標記
            return
        elif abs(p1.x - p2.x) >= abs(p1.y - p2.y):
            if p1.x > p2.x:
                begin, end = p2, p1
            elif p1.x < p2.x:
                begin, end = p1, p2
            slope = np.float(end.y - begin.y) / (end.x - begin.x)
            yFloat = float(begin.y)
            for x1 in range(begin.x, end.x, 1):
                if (x1 >= 0) and (x1 < self.Width):
                    y1 = int(round(yFloat))
                    if (y1 >= 0) and (y1 < self.Height):
                        self.Data[x1, y1] = 254
                    yFloat = yFloat + slope
        else:
            if p1.y > p2.y:
                begin, end = p2, p1
            elif p1.y < p2.y:
                begin, end = p1, p2
            slope = np.float(end.x - begin.x) / (end.y - begin.y)
            xFloat = float(begin.x)
            for y1 in range(begin.y, end.y, 1):
                if (y1 >= 0) and (y1 < self.Height):
                    x1 = int(round(xFloat))
                    if (x1 >= 0) and (x1 < self.Width):
                        self.Data[x1, y1] = 254
                    xFloat = xFloat + slope

    def drawCircleSolid(self, x, y, r):
        r2 = r * r
        for y1 in range(0, r + 1):
            x1 = int(np.sqrt(r2 - y1 * y1))
            self.drawLine(Point(x - x1, y + y1), Point(x + x1, y + y1))
            self.drawLine(Point(x - x1, y - y1), Point(x + x1, y - y1))
