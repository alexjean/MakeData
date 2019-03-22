# -*- coding: utf-8 -*-
# @Time    : 2018/11/5 下午 06:22
# @Author  : AlexJean
import numpy as np
from PyQt5.QtWidgets import QApplication


class GaCo:
    """
    要制作的TrainData output
    改為 每個點一個 強度 (梯度?)  offset 定義如Dir9 <= stride2 shift
    鄰居8點加自己投票定,本'田字'最sharp offset. 但offset只用於本點
    暫不處理SuperResolution, 能力不足
    """
    IsEdge = 1
    NotEdge = 0
    Dir9 = [[0, 0], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]]
    Dir8 = [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]]

    def __init__(self, w, h, shinkFactor):
        self.marked = np.zeros((w, h), np.uint16)
        self.Wid = w
        self.Hei = h
        self.Factor = shinkFactor
        self.stride2Factor = shinkFactor // 2
        # below variables  for evaluateStride2Map
        self.W2 = w // self.stride2Factor - 1
        self.H2 = h // self.stride2Factor - 1
        stride2dim = (self.W2, self.H2)
        self.stride2 = np.zeros(stride2dim, np.int16)
        self.worldData = None
        self.trainLabel = None
        self.contrastData = np.zeros(stride2dim, np.int32)
        self.forbidLevel = np.zeros(stride2dim, np.int32)
        self.forbidBy = np.zeros(stride2dim, np.object)

    @staticmethod
    def echo(x, format_str="%d"):
        print(format_str % x, end=' ', flush=True)
        QApplication.processEvents()

    def getEdgePoint(self, data):
        print('Begin getEdgeList '+'=' * 31)
        da = np.array(data)
        for x in range(1, self.Wid):
            if x % 10 == 0:
                print("%4d" % x, end=' ', flush=True)
                if x % 100 == 0:
                    print(' ')
            for y in range(1, self.Hei):
                if self.marked[x, y] == GaCo.NotEdge:
                    x1, y1 = x - 1, y - 1
                    c, up, left = da[x, y], da[x, y1], da[x1, y]
                    if c != up or c != left:
                        self.markEdge(x, y)
                        self.checkEdge(c, up, x, y1)
                        self.checkEdge(c, left, x1, y)
        c, right, down = da[0, 0], da[1, 0], da[0, 1]
        if c != down or c != right:
            self.markEdge(0, 0)
            self.checkEdge(c, down, 0, 1)
            self.checkEdge(c, right, 1, 0)
        print('\nend of getEdgeList')
        return

    def markEdge(self, x, y):
        self.marked[x, y] = GaCo.IsEdge

    def checkEdge(self, me, other, x, y):
        if me == other:  # 二點同色
            return False
        if self.marked[x, y] == GaCo.IsEdge:  # 己被標記是edge
            return False
        self.markEdge(x, y)

    def valueEdge(self, x, y):
        # IsEdge = 1 所以可用np.sum() , 現在6*6縮小, *10有可能大於255了
        val = np.sum(self.marked[x:x+self.Factor, y:y+self.Factor])
        return val if val < 25 else 25

    def evaluateDiv4Map(self, data):
        print("Begin valueShrinkMap ============")
        w, h = self.Wid // self.Factor, self.Hei // self.Factor
        for x in range(w):
            if x % 20 == 0:
                GaCo.echo(x)
            for y in range(h):
                data[x, y] = self.valueEdge(x * self.Factor, y * self.Factor) * 10
        print("\ncompleted!")

    def evaluateStride2Map(self):
        print("Begin valueStride2Map "+'='*51)
        w2, h2 = self.W2, self.H2
        for x in range(0, w2):
            if x % 20 == 0:
                GaCo.echo(x)
            for y in range(0, h2):
                self.stride2[x, y] = self.valueEdge(x * self.stride2Factor, y * self.stride2Factor)  # 這個值拿來算Variance的,先不乘10
        print("\ncompleted!")

    def evaluateAllContrast(self):
        print("Begin valueAllContrast " + '=' * 56)
        w2, h2 = self.W2, self.H2
        for x in range(2, w2-2):
            if x % 10 == 0:
                GaCo.echo(x, "%3d")
                if x % 200 == 0:
                    print(' ')
            for y in range(2, h2-2):
                self.contrastData[x, y] = self.contrast(x, y)
        print("\ncompleted!")

    def renewForbidden(self, x, y):
        maxLevel, pos = 0, 0
        for di in GaCo.Dir8:
            x1, y1 = x + di[0], y + di[1]
            if self.forbidLevel[x1, y1] > maxLevel:  # 有佔位
                maxLevel = self.forbidLevel[x1, y1]
                pos = (x1, y1)
        self.forbidLevel[x, y] = -maxLevel           # 正數是佔位,負數是禁區
        self.forbidBy[x, y] = pos

    def setWorldData(self, x, y):
        # self.stride2內存的是16pixels 白邊+黑邊+較短的邊,所以不可能超過24
        # 現在不分黑白, 所以不可能超過16
        self.worldData[x, y] = grayLevel = self.stride2[x, y] * 10
        x0, y0 = x // 2, y // 2
        if grayLevel == 0:
            self.trainLabel[x0, y0] = 0
        else:
            x1, y1 = x % 2, y % 2
            self.trainLabel[x0, y0] = (x1 << 12) + (y1 << 8) + grayLevel

    def clearWorldData(self, x, y):
        self.worldData[x, y] = 0
        self.trainLabel[x // 2, y // 2] = 0

    def clearPosition(self, x, y):
        self.clearWorldData(x, y)
        self.renewForbidden(x, y)
        pos = (x, y)
        for di in GaCo.Dir8:
            x1, y1 = x + di[0], y + di[1]
            if self.forbidBy[x1, y1] == pos:   # 自己要清0, 為禁區找新東家
                self.renewForbidden(x1, y1)

    def markForbidden(self, x, y, forbidLevel, warning=True):
        relist = []
        pos = (x, y)
        for di in GaCo.Dir8:
            x2, y2 = x + di[0], y + di[1]
            level = self.forbidLevel[x2, y2]
            if level == 0:
                self.forbidBy[x2, y2] = pos
                self.forbidLevel[x2, y2] = -forbidLevel
            elif level > 0:                     # 有人佔位
                if level > forbidLevel:         # 人家強 , 外面有檢查最強才進來,應該不可能
                    if warning:
                        print("Err2({},{})".format(x, y))
                else:                           # 我們強, 清除他
                    x3, y3 = self.forbidBy[x2, y2]
                    relist.append((x3, y3))
                    self.clearPosition(x3, y3)
            elif (-level) > forbidLevel:        # 別人禁區較強 ^^" 繞開
                pass
            else:
                self.forbidBy[x2, y2] = pos     # 我們強, 改我們禁區
                self.forbidLevel[x2, y2] = -forbidLevel
        self.forbidLevel[x, y] = forbidLevel
        self.forbidBy[x, y] = pos
        return relist

    def rePosList(self, relist):
        for (x, y) in relist:
            x1, y1 = x - (x % 2), y - (y % 2)
            x2, y2, var = self.maxContrastPartial(x1, y1)
            if var > 0:  # <=0 無路可走
                relist1 = self.markForbidden(x2, y2, var, False)  # 此處不warning了
                self.setWorldData(x2, y2)
                self.rePosList(relist1)

    def evaluateSmartDiv4Map(self, stride2world, div4World):
        self.evaluateStride2Map()      # data put in self.stride2
        self.evaluateAllContrast()
        print("Begin fill stride2world "+'='*42)
        w, h = self.Wid // self.Factor, self.Hei // self.Factor
        stride2world.clearWorld()
        self.worldData = stride2world.Data
        self.trainLabel = div4World.trainLabel                        # 呼叫方初使己有 = np.zero((w,h),np.int16)
        # int16 highByte是offset,編碼如同 Gaco.Dir9 =>(-1, 1)
        # lowByte是GrayLevel

        for x in range(2, w-2):
            if x % 10 == 0:
                GaCo.echo(x)
            for y in range(2, h-2):
                x1, y1 = x * 2, y * 2
                x2, y2, var = self.maxContrastAll(x1, y1)
                if var <= 0:
                    continue
                level = self.forbidLevel[x2, y2]
                if level == 0:                                        # 此點無禁制
                    relist = self.markForbidden(x2, y2, var)
                elif level > 0 or (-level) >= var:                    # 鄰居本尊, 佔同一位置Contrast必相同, 故讓
                    x2, y2, var = self.maxContrastPartial(x1, y1)     # or 鄰居禁區, 鄰居強 , 重定位
                    if var <= 0:                                      # 無路可走
                        continue
                    relist = self.markForbidden(x2, y2, var)
                else:                                                 # else 鄰居禁區, 鄰居弱, 鄰居重算
                    x3, y3 = self.forbidBy[x2, y2]
                    self.clearPosition(x3, y3)
                    relist = self.markForbidden(x2, y2, var)          # 此處或有第二鄰居,沖禁制
                    relist.insert(0, (x3, y3))
                self.setWorldData(x2, y2)
                self.rePosList(relist)                           # recursive call
        print("\ncompleted!")
        stride2world.repaint()

#    def stride2Label(self, stride2World, div4World):
#        w, h = self.Wid // self.Factor, self.Hei // self.Factor
#        label = div4World.trainLabel = np.zeros((w, h), np.uint16)
        # uint16 highByte是offset,編碼如同 Gaco.Dir9
        # lowByte是GrayLevel
#        data = stride2World.Data
#        for x in range(2, w-2):
#            for y in range(2, h-2):
#                x1, y1 = x * 2, y * 2

    def maxContrastPartial(self, x1, y1):
        maxVar, mX, mY = -1, x1, y1
        for di in GaCo.Dir9:
            x, y = x1 + di[0], y1 + di[1]
            if self.forbidLevel[x, y] == 0:      # 負數代表己經被禁止了, 正數代表有點了
                var = self.contrastData[x, y]
                if var > maxVar:
                    maxVar, mX, mY = var, x, y
        return mX, mY, maxVar

    def maxContrastAll(self, x1, y1):
        maxVar, mX, mY = -1, x1, y1
        for di in GaCo.Dir9:
            x, y = x1 + di[0], y1 + di[1]
            var = self.contrastData[x, y]
            if var > maxVar:
                maxVar, mX, mY = var, x, y
        return mX, mY, maxVar

    # x,y 算二次, 加其他8方向,湊成10
    def contrast(self, x, y):
        v = self.stride2
        direction = [[2, 0], [2, 2], [0, 2], [-2, 2], [-2, 0], [-2, -2], [0, -2], [2, -2]]
        u = v[x, y] * 2
        for di in direction:
            u += v[x + di[0], y + di[1]]
        var = GaCo.variance(v[x, y] * 10, u) * 2
        for di in direction:
            var += GaCo.variance(v[x+di[0], y + di[1]] * 10, u)
        return var

    # int pow2
    @staticmethod
    def variance(val, u):
        z = val - u
        return z * z
