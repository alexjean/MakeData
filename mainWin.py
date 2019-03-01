# -*- coding: utf-8 -*-
# @Time    : 2018/8/20 下午 03:29
# @Author  : AlexJean
import sys
from PyQt5.QtWidgets import *
from Ui_mainWin import *
#from DigiWorld import *
from AnalogWorld import *
from Point import Point
import numpy as np
from World import World
import random
import os
import time

class Form(Ui_Dialog, QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setupUi(self)
        self.move(450, 40)
        w, h = 200, 200
        self.Wid, self.Hei = w * 4, h * 4
        self.view.resize(w + 4, h + 4)
        self.view1.move(self.view.x() + w + 4, self.view.y())
        self.view1.resize(w + 4, h + 4)
        self.view2.move(self.view.x()+2, self.view.y()+self.view.height() + 4)
        self.view2.resize(w*2 + 4, h*2 + 4)
        self.viewLarge.resize(w*4 + 4, h*4 + 4)
        self.viewLarge.move(self.view1.x() + w + 8, self.view.y())

        self.world = AnalogWorld(self.view, self.viewLarge, w, h)
        self.loadedWorld = Div4World(self.view1, w, h)   # 給 loadData做檢查
        # self.world = DigiWorld(self.view, self.view1, self.viewLarge, w, h)
        self.loadedData = None
        self.stride2World = World(self.view2, w*2, h*2)

    def doCircle(self):
        x = self.world.Width // 2
        y = self.world.Height // 2
        r = self.world.Width // 3
        self.world.drawCircle(x, y, r)
        self.world.drawCircle(x, y, r // 2, 0)
        self.world.before_repaint()
        self.world.repaint()

    def doLine(self):
        a = Point(0, 0)
        b = Point(self.world.Width, self.world.Height)
        c = Point(0, self.world.Height)
        d = Point(self.world.Width // 2, 0)
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
        self.world.calcGamaLabel(self.loadedWorld, self.stride2World)    # 算出來的TtrainData填到loadedWorld.Data驗証

    def clearWorld(self):
        self.world.clearWorld()
        self.loadedWorld.clearWorld()
        self.stride2World.clearWorld()

    def fileName(self):
        name = 'data/' + self.leTrainFileName.text()
        name += "{:0>4d}".format(self.sboxTrainFileName.value()) + '.npz'
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
            self.stride2World.clearWorld()
            Form.label2stride2(self.loadedWorld, self.stride2World.Data)
            self.stride2World.repaint()
            print(name + ' data' + str(da.shape) + ' label' + str(la.shape) + ' loaded!')
        except Exception as reason:
            strReason = str(reason)
            print(strReason)

    @staticmethod
    def label2stride2(loadedWorld, data):
        label = loadedWorld.trainLabel
        for row in range(loadedWorld.Width):
            for col in range(loadedWorld.Height):
                la = label[row, col]
                co = la & 0xff
                x0, y0 = la >> 12, (la >> 8) & 0xf
                x, y = row*2+x0, col*2+y0
                data[x, y] = co

    def randomLine(self):
        x0 = random.randint(1, self.Wid - 2)
        y0 = random.randint(1, self.Hei - 2)
        x1 = random.randint(1, self.Wid - 2)
        y1 = random.randint(1, self.Hei - 2)
        wi = random.randint(10, 100)
        co = 0 if random.randint(0, 2) == 0 else 254
        if abs(y1 - y0) > abs(x1 - x0):
            for i in range(wi):
                self.world.drawLine(Point(x0 + i, y0), Point(x1 + i, y1), co)
        else:
            for i in range(wi):
                self.world.drawLine(Point(x0, y0 + i), Point(x1, y1 + i), co)

    def randomCircle(self):
        x = random.randint(1, self.Wid - 2)
        y = random.randint(1, self.Hei - 2)
        r = random.randint(10, self.Wid // 3)
        co = 0 if random.randint(0, 2) == 0 else 254
        self.world.drawCircle(x, y, r, co)

    def doGenerate(self):
        for no in range(30):
            if random.randint(0, 2) == 0:
                self.randomCircle()
            else:
                self.randomLine()

        self.world.before_repaint()
        self.world.repaint()

    def doAuto(self):
        if not os.path.exists('data'):
            os.mkdir('data')
        pathName = self.edPath.text().strip()
        dirName = "data/"+pathName
        if os.path.exists(dirName):
            QMessageBox.information(self, "Info", "目錄<"+dirName+">己經存在, 請指定新的目錄名!")
        else:
            os.mkdir(dirName)
            QMessageBox.information(self, "Info", "目錄<"+dirName+">己建立, 開始創造訓練資料!")
            self.leTrainFileName.setText(pathName+"/"+pathName)
            for i in range(1000):
                self.sboxTrainFileName.setValue(i)
                self.clearWorld()
                self.doGenerate()
                self.calcTrainLabel()
                self.saveTrainData()
                time.sleep(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Form()
    win.show()
    sys.exit(app.exec())
