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
import Neural
import torch
import matplotlib.pyplot as plt


def Statistics(func):
    def wrapper(self):
        start = time.time()
        stat = func(self)
        secs = time.time() - start
        print("Function %s takes %d seconds!" % (func.__name__, secs))
        if not (stat is None):
            plt.plot(stat)
            plt.show()
    return wrapper


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

    def fileName(self, intVal=-1):
        name = 'data/' + self.leTrainFileName.text()
        if intVal < 0:
            name += "{:0>4d}".format(self.sboxTrainFileName.value()) + '.npz'
        else:
            name += "{:0>4d}".format(intVal) + '.npz'
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

    def doLoadData(self):
        if self.loadData(self.fileName()):
            self.loadedWorld.Data = self.loadedData['data']
            self.loadedWorld.trainLabel = self.loadedData['label']
            self.loadedWorld.repaint()
            self.stride2World.clearWorld()
            Form.label2stride2(self.loadedWorld.trainLabel, self.stride2World.Data)
            self.stride2World.repaint()

    def loadData(self, name):
        try:
            self.loadedData = np.load(name)
            da = self.loadedData['data']
            la = self.loadedData['label']
            print(name + ' data' + str(da.shape) + ' label' + str(la.shape) + ' loaded!')
            QApplication.processEvents()
            return True
        except Exception as reason:
            strReason = str(reason)
            print(strReason)
            return False

    @staticmethod
    def newColor(co):
        """
        1點:2點:10點:12點 發生率約 2.7: 1: 2.5: 8.5 其餘都接近0
        大於12以上的可能是特徴點
        故將10點含以上定為3 = 0.99  , 1 2 點的全忽略
        """
        if co < 33:
            return 0
        elif co > 99:
            return 3
        elif co > 66:
            return 2
        else:
            return 1

    @staticmethod
    def label2stride2(label, data):
        (h, w) = label.shape
        for row in range(h):
            for col in range(w):
                la = label[row, col]
                x0, y0 = la >> 12, (la >> 8) & 0xf
                x, y = row * 2 + x0, col * 2 + y0
                co = la & 0xff
                # data[x, y] = Form.newColor(co) * 50
                data[x, y] = 0 if co < 40 else 150  # 1 2 3全顯示150

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

    def doBatchGenerateLabel(self):
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

    @Statistics
    def doMergeData(self):
        """
        data/AA/AA0000.npz
        data = [1, 200, 200]  int32 只用了uint8
        label = [200,200] uint16=00xx00yy cccccccc, 最小編碼為onehot可用4個bit,全0 或最多一個1
        為方便取batch, 將檔案merge為
        data = [batch,1,200,200]  uint8
        label = [batch,1,200,200] uint8  ,4output每個output佔2bit空間
        """
        pathName = self.edPath.text().strip()
        dirName = "data/" + pathName
        if not os.path.exists(dirName):
            QMessageBox.information(self, "Info", "目錄<"+dirName+">不存在, 請指定新的目錄名!")
            return None
        files = os.listdir(dirName)
        batch = len(files)
        self.loadData(dirName+'/'+files[0])
        (h, w) = self.loadedData['data'].shape
        data = np.zeros([batch, 1, h, w], np.uint8)
        label = np.zeros([batch, 1, h, w], np.uint8)
        i = 0
        stat = np.zeros([26], np.int32)
        for fi in files:
            if not fi.lower().endswith('.npz'):
                continue
            self.loadData(dirName+'/'+fi)
            da = self.loadedData['data']
            la = self.loadedData['label']
            data[i, 0] = da.astype(np.uint8)
            li0 = label[i, 0]
            for row in range(h):
                for col in range(w):
                    l1 = la[row, col]
                    co = l1 & 0xff
                    if co != 0:              # 0 太多了
                        stat[co//10] += 1    # co是16點計邊 * 10來的
                    x = (l1 >> 12) & 1
                    y = (l1 >> 8) & 1
                    b1 = Form.newColor(co) << (4 * x + 2 * y)         # 3=0.99   2=0.66  1=0.33  0 = 0
                    li0[row, col] = b1 & 0xff
            i = i + 1
        name = "data/Full"+pathName+".npz"
        try:
            np.savez_compressed(name, data=data, label=label)
            print(name + " write success!")
        except Exception as reason:
            print('Error:' + str(reason))
        return stat

    @staticmethod
    def translateLabel(label):
        """ from [batch,1,H,W] uint8 to [batch,4,H,W] float
        """
        # toFloat = (0.0, 0.33, 0.66, 0.99)
        sh = label.shape
        batch = sh[0]
        H = sh[2]
        W = sh[3]
        la = torch.LongTensor(batch, 1, H, W)   # 不管邊的強弱了, 0 或4個位置選1 , 五選一
        for n in range(batch):
            ln = label[n, 0]
            lan = la[n, 0]
            for row in range(H):
                for col in range(W):
                    val = ln[row, col]
                    if val == 0:
                        lan[row, col] = 0
                    elif (val & 3) != 0:
                        lan[row, col] = 1
                    elif (val & 12) != 0:
                        lan[row, col] = 2
                    elif (val & 48) != 0:
                        lan[row, col] = 3
                    else:
                        lan[row, col] = 4
        return la

    def doTraining(self):
        pathName = self.edPath.text().strip()
        name = "data/Full" + pathName + ".npz"
        loaded = np.load(name)
        data = loaded["data"].astype(float)/255.0
        label = loaded["label"]
        n = len(data)
        batch = 20
        net = Neural.Net()
        optimizer = torch.optim.Adam(net.parameters(), lr=Neural.Net.LearningRate)
        lossFunc = torch.nn.CrossEntropyLoss()
        for i in range(0, n, batch):
            print(i, end=' ', flush=True)
            x = torch.FloatTensor(data[i:i+batch])
            print('+', end=' ', flush=True)
            y = Form.translateLabel(label[i:i+batch])
            print('*', end=' ', flush=True)
            pred_y = net.forward(x)
            loss = lossFunc(pred_y, y)
            print("<%3d> %.4f" % (i, loss))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Form()
    win.show()
    sys.exit(app.exec())
