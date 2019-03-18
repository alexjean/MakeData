# -*- coding: utf-8 -*-
# @Time    : 2018/8/20 下午 03:29
# @Author  : AlexJean
import sys
from PyQt5.QtWidgets import *
from Ui_mainWin import *
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
        self.view2.move(self.view.x() + 2, self.view.y() + self.view.height() + 4)
        self.view2.resize(w * 2 + 4, h * 2 + 4)
        self.viewLarge.resize(w * 4 + 4, h * 4 + 4)
        self.viewLarge.move(self.view1.x() + w + 8, self.view.y())

        self.world = AnalogWorld(self.view, self.viewLarge, w, h)
        self.loadedWorld = Div4World(self.view1, w, h)  # 給 loadData做檢查
        # self.world = DigiWorld(self.view, self.view1, self.viewLarge, w, h)
        self.loadedData = None
        self.stride2World = World(self.view2, w * 2, h * 2)

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
        # self.world.calcAlphaLabel()
        # self.world.calcBetaLabel()
        self.world.calcGamaLabel(self.loadedWorld, self.stride2World)  # 算出來的TtrainData填到loadedWorld.Data驗証

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

    def doSaveData(self):
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

    def randomLine(self, colorList):
        x0 = random.randint(1, self.Wid - 2)
        y0 = random.randint(1, self.Hei - 2)
        x1 = random.randint(1, self.Wid - 2)
        y1 = random.randint(1, self.Hei - 2)
        wi = random.randint(10, 100)
        co = colorList[random.randrange(0, len(colorList))]
        # co = 0 if random.randint(0, 2) == 0 else 254
        if abs(y1 - y0) > abs(x1 - x0):
            for i in range(wi):
                self.world.drawLine(Point(x0 + i, y0), Point(x1 + i, y1), co)
        else:
            for i in range(wi):
                self.world.drawLine(Point(x0, y0 + i), Point(x1, y1 + i), co)

    def randomCircle(self, colorList):
        x = random.randint(1, self.Wid - 2)
        y = random.randint(1, self.Hei - 2)
        r = random.randint(10, self.Wid // 3)
        co = colorList[random.randrange(0, len(colorList))]
        # co = 0 if random.randint(0, 2) == 0 else 254
        self.world.drawCircle(x, y, r, co)

    def RandDraw(self, colorList=[0, 254, 254]):
        for no in range(30):
            if random.randint(0, 2) == 0:
                self.randomCircle(colorList)
            else:
                self.randomLine(colorList)
        self.world.before_repaint()
        self.world.repaint()

    def doRandDraw(self):
        colorList = [0, 64, 128, 192, 254] if self.comboGrey.currentText().strip().lower() == 'grey' else [0, 254, 254]
        self.RandDraw(colorList)


    def doPatch(self):
        QMessageBox.information(None, "Info", "開始補足data目錄內未完成Generate!")
        dirs = os.listdir("data/")
        for di in dirs:
            subdir = "data/" + di
            if os.path.isdir(subdir):
                sublist = os.listdir(subdir)
                lenSub = len(sublist)
                print("Dir<%s> Total %d " % (subdir, lenSub))
                if lenSub < 1000:
                    for i in range(lenSub - 1 if lenSub > 0 else 0, 1000):
                        # 覆蓋最後一個, 沒完成可能最後一個也是壞的
                        self.generateOne(di, i)

    def checkDataDir(self):
        if not os.path.exists('data'):
            os.mkdir('data')
        pathName = self.edPath.text().strip()
        dirName = "data/" + pathName
        if os.path.exists(dirName):
            QMessageBox.information(None, "Info", "目錄<" + dirName + ">己經存在, 請指定新的目錄名!")
            return ''
        else:
            os.mkdir(dirName)
            QMessageBox.information(None, "Info", "目錄<" + dirName + ">己建立, 開始創造訓練資料!")
            return pathName

    def generateOne(self, pathName, i):
        self.leTrainFileName.setText(pathName + "/" + pathName)
        self.sboxTrainFileName.setValue(i)
        self.clearWorld()
        self.doRandDraw()
        self.calcTrainLabel()
        self.doSaveData()
        QApplication.processEvents()

    @Statistics
    def doBatchCalcLabel(self):
        pathName = self.checkDataDir()
        if pathName == '':
            return None
        for i in range(1000):
            self.generateOne(pathName, i)
        return None

    def paddingNameClassNo(self, padding):
        if self.comboClassNo.currentText().strip() == '5':
            classNo = 5
        else:
            classNo = 2
        pathName = self.edPath.text().strip()
        fullName = "data/" + padding + pathName + str(classNo) + ".npz"
        return fullName, classNo

    @Statistics
    def doMergeData(self):
        """
        data/AA/AA0000.npz
        data = [1, 200, 200]  int32 只用了uint8
        label = [200,200] uint16=00xx00yy cccccccc, 最小編碼為onehot可用4個bit,全0 或最多一個1
        為方便取batch, 將檔案merge為
        data = [batch,1,200,200]  uint8
        label = [batch,200,200] uint8  , [0...4] graylevel ignore
        """
        pathName = self.edPath.text().strip()
        dirName = "data/" + pathName
        if not os.path.exists(dirName):
            QMessageBox.information(self, "Info", "目錄<" + dirName + ">不存在, 請指定新的目錄名!")
            return None
        files = os.listdir(dirName)
        batch = len(files)
        self.loadData(dirName + '/' + files[0])
        (h, w) = self.loadedData['data'].shape
        data = np.zeros([batch, 1, h, w], np.uint8)
        label = np.zeros([batch, h, w], np.uint8)
        i = 0
        stat = np.zeros([26], np.int32)
        fullName, classNo = self.paddingNameClassNo("Full")
        for fi in files:
            if not fi.lower().endswith('.npz'):
                continue
            self.loadData(dirName + '/' + fi)
            da = self.loadedData['data']
            la = self.loadedData['label']
            data[i, 0] = da.astype(np.uint8)
            li0 = label[i]
            for row in range(h):
                for col in range(w):
                    l1 = la[row, col]
                    co = l1 & 0xff
                    if co != 0:  # 0 太多了
                        stat[co // 10] += 1  # co是16點計邊 * 10來的
                    # 原本為保留grayLevel 0...3的編碼
                    # x = (l1 >> 12) & 1
                    # y = (l1 >> 8) & 1
                    # b1 = Form.newColor(co) << (4 * x + 2 * y)         # 3=0.99   2=0.66  1=0.33  0 = 0
                    # li0[row, col] = b1 & 0xff
                    if co >= 40:  # < 40 編碼 0
                        if classNo == 2:
                            li0[row, col] = 1
                        else:
                            x = (l1 >> 12) & 1
                            y = (l1 >> 8) & 1
                            li0[row, col] = 2 * x + y + 1  # 有, 依位置編1..4  共5 classes

            i = i + 1
        try:
            np.savez_compressed(fullName, data=data, label=label)
            print(fullName + " write success!")
        except Exception as reason:
            print('Error:' + str(reason))
        return stat

    def showPredict(self, data, pred):
        H = data.shape[0]
        W = data.shape[1]
        self.world.div4World.Data = data
        self.world.div4World.repaint()
        # pred2Draw = np.zeros((H, W), np.uint8)
        if pred.shape[0] == 2:
            pred2Draw = torch.argmax(pred, 0).cpu().numpy() * 150
            self.loadedWorld.Data = pred2Draw
            self.loadedWorld.repaint()
        else:
            label = torch.argmax(pred, 0).cpu().numpy()
            pred2Draw = np.zeros((H * 2, W * 2), np.uint8)
            for row in range(H):
                for col in range(W):
                    cl = label[row, col]
                    if cl == 0:
                        continue
                    h2, w2 = row * 2, col * 2
                    if cl == 1:
                        pred2Draw[h2, w2] = 150
                    elif cl == 2:
                        pred2Draw[h2, w2 + 1] = 150
                    elif cl == 3:
                        pred2Draw[h2 + 1, w2] = 150
                    elif cl == 4:
                        pred2Draw[h2 + 1, w2 + 1] = 150
            self.stride2World.Data = pred2Draw
            self.stride2World.repaint()

    @Statistics
    def doTraining(self):
        fullName, classNo = self.paddingNameClassNo("Full")
        if not os.path.exists(fullName):
            QMessageBox.information(None, "Info", "檔案" + fullName + " 不存在!")
            return None
        elif not os.path.isfile(fullName):
            QMessageBox.information(None, "Info", "<" + fullName + "> 不是檔案!")
            return None
        print("Loading data from " + fullName)
        loaded = np.load(fullName)
        # data = loaded["data"].astype(float)/255.0
        data = loaded["data"]
        label = loaded["label"]
        n = len(data)
        batch = 1
        net = Neural.Net(classNo).cuda()
        optimizer = torch.optim.Adam(net.parameters(), lr=Neural.Net.LearningRate)
        lossFunc = torch.nn.CrossEntropyLoss().cuda()
        for i in range(0, n, batch):
            print("<%03d>" % (i // batch), end=' ', flush=True)
            byteData = data[i:i + batch]
            x = torch.cuda.FloatTensor(byteData.astype(float) / 255.0)
            print('+', end=' ', flush=True)
            y = torch.cuda.LongTensor(label[i:i + batch])
            print('*', end=' ', flush=True)
            pred_y = net.forward(x)
            loss = lossFunc(pred_y, y)  # pred_y : FloatTensor(N,C,H,W)  where C = number of classes
            #  y      : LongTensor(N,H,W)     where each value in range(C) .
            print("%.4f " % loss, end=' ', flush=True)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            print(' ')
            if self.chBoxDrawPredict.isChecked():
                self.showPredict(byteData[0, 0], pred_y[0])
            QApplication.processEvents()
        try:
            netName, _ = self.paddingNameClassNo("Net")
            np.savez_compressed(netName, net=net.cpu())
            print(netName + " write success!")
        except Exception as reason:
            print('Error:' + str(reason))
        return None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Form()
    win.show()
    sys.exit(app.exec())
