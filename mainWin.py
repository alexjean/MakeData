# -*- coding: utf-8 -*-
# @Time    : 2018/8/20 下午 03:29
# @Author  : AlexJean
import sys
from PyQt5.QtWidgets import *
from Ui_mainWin import *
from DigiWorld import *
from AnalogWorld import *
from Point import Point
import numpy as np


class Form(Ui_Dialog, QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setupUi(self)
        w = 200
        h = 200
        self.view.resize(w + 4, h + 4)
        self.view1.move(self.view.x(), self.view.y() + self.view.height() + 1)
        self.view1.resize(w + 4, h + 4)
        self.viewLarge.resize(w * 4 + 4, h * 4 + 4)
        self.viewLarge.move(self.view.x() + w + 8, self.view.y())
        self.world = AnalogWorld(self.view, self.viewLarge, w, h)
        self.loadedWorld = Div4World(self.view1, w, h)   # 給 loadData做檢查
        #self.world = DigiWorld(self.view, self.view1, self.viewLarge, w, h)
        self.loadedData = None

    def doLine(self):
        a = Point(0, 0)
        b = Point(self.world.Width, self.world.Height)
        c = Point(0, self.world.Height)
        d = Point(self.world.Width, 0)
        scale = 3
        for i in range(6 * scale):
            ofs = Point(i, 0)
            self.world.drawLine(a + ofs, b + ofs)
            self.world.drawLine(c + ofs, d + ofs)

        h = self.world.Height - 10 * scale
        for x in range(10 * scale, self.world.Width, 37 * scale):
            for i in range(4 * scale):
                self.world.drawLine(Point(x + i + 1, 10), Point(x + i + 1, h))

        self.world.before_repaint()
        self.world.repaint()

    def calcTrainLabel(self):
        #self.world.calcAlphaLabel()
        #self.world.calcBetaLabel()
        self.world.calcGamaLabel(self.loadedWorld)    # 算出來的TtrainData填到loadedWorld.Data驗証

    def clearWorld(self):
        self.world.clearWorld()

    def fileName(self):
        name = 'data/' + self.leTrainFileName.text() + '_'
        name += str(self.sboxTrainFileName.value()) + '.npz'
        return name

    def saveTrainData(self):
        name = self.fileName()
        try:
            np.savez_compressed(name, data=self.world.div4World.Data, label=self.world.div4World.trainLabel)
            print(name + " write success!")
        except Exception as reason:
            print('Error:' + str(reason))
        print(name + " Saved!")
        # self.sboxTrainFileName.stepUp()
        self.btnSave.setFocus()

    def loadData(self):
        name = self.fileName()
        try:
            self.loadedData = np.load(name)
            da = self.loadedData['data']
            la = self.loadedData['label']
            self.loadedWorld.Data = da
            self.loadedWorld.trainLabel = la
            self.loadedWorld.repaint()
            print(name + ' data' + str(da.shape) + ' label' + str(la.shape) + ' loaded!')
        except Exception as reason:
            print('Error:' + str(reason))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Form()
    win.show()
    sys.exit(app.exec())
