# -*- coding: utf-8 -*-
# @Time    : 2018/9/7 下午 02:02
# @Author  : AlexJean
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt


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
        if p1.x > p2.x:
            begin = p2
            end = p1
        elif p1.x < p2.x:
            begin = p1
            end = p2
        else:
            x1 = p1.x
            if (x1 < 0) or (x1 >= self.Width):
                return
            if p1.y > p2.y:
                begin = p2
                end = p1
            else:
                begin = p1
                end = p2
            if (begin.y >= self.Height) or (end.y < 0):
                return
#            print("Line(%s,%s) (%s,%s) created!" % (begin.x, begin.y, end.x, end.y))
            if begin.y < 0:
                begin.y = 0
            if end.y > self.Height:
                end.y = self.Height
            for y1 in range(begin.y, end.y, 1):
                self.Data[x1, y1] = 254  # 暫時保留255, 做特別標記
            return
        slope = np.float(end.y - begin.y) / (end.x - begin.x)
        yFloat = float(begin.y)
        for x1 in range(begin.x, end.x, 1):
            if (x1 >= 0) and (x1 < self.Width):
                y1 = int(round(yFloat))
                if (y1 >= 0) and (y1 < self.Height):
                    self.Data[x1, y1] = 254
                yFloat = yFloat + slope
#        print("Line(%s,%s) (%s,%s) created!" % (begin.x, begin.y, end.x, end.y))
