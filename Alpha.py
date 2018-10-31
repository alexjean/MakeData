# -*- coding: utf-8 -*-
# @Time    : 2018/10/11 下午 05:09
# @Author  : AlexJean
# 此種編碼失敗了 要保存的是邊線角度
# 不是SuperResolution或灰度面積最小誤差
from typing import Any, Union

import numpy as np


class AlphaCode:
    Dtype = np.int16
    TableSize = 26
    Table = np.empty((TableSize, 4, 4), Dtype)
    Shape = (4, 4)
    zeros = np.zeros(Shape, Dtype)
    w = 127
    b = -127
    BlackPlate = 0
    WhitePlate = 13
    Table[BlackPlate] = np.array([[b, b, b, b], [b, b, b, b], [b, b, b, b], [b, b, b, b]], Dtype)
    Table[WhitePlate] = zeros - Table[BlackPlate]
    Table[1] = np.array([[w, w, w, w], [w, w, w, b], [w, w, b, b], [w, b, b, b]], Dtype)  # 採取白的往前佔
    Table[2] = np.array([[w, b, b, b], [w, w, b, b], [w, w, w, b], [w, w, w, w]], Dtype)  # 採取白的往前佔
    Table[14] = np.array([[b, b, b, w], [b, b, w, w], [b, w, w, w], [w, w, w, w]], Dtype)  # 採取白的往前佔
    Table[15] = np.array([[w, w, w, w], [b, w, w, w], [b, b, w, w], [b, b, b, w]], Dtype)  #採取白的往前佔
    Table[3] = np.array([[w, w, w, b], [w, b, b, b], [b, b, b, b], [b, b, b, b]], Dtype)
    Table[4] = np.array([[w, w, w, w], [w, w, w, b], [w, w, w, b], [w, w, b, b]], Dtype)
    Table[5] = np.array([[b, b, b, b], [w, b, b, b], [w, b, b, b], [w, w, b, b]], Dtype)
    Table[6] = np.array([[w, b, b, b], [w, w, w, b], [w, w, w, w], [w, w, w, w]], Dtype)
    Table[7] = np.array([[w, w, w, w], [w, w, w, w], [b, b, b, b], [b, b, b, b]], Dtype)
    Table[8] = np.array([[w, w, w, w], [w, w, w, w], [w, w, w, b], [w, b, b, b]], Dtype)
    Table[9] = np.array([[w, w, w, w], [w, w, w, w], [b, w, w, w], [b, b, b, w]], Dtype)
    Table[10] = np.array([[w, w, b, b], [w, b, b, b], [w, b, b, b], [b, b, b, b]], Dtype)
    Table[11] = np.array([[w, w, b, b], [w, w, w, b], [w, w, w, b], [w, w, w, w]], Dtype)
    Table[12] = np.array([[w, w, b, b], [w, w, b, b], [w, w, b, b], [w, w, b, b]], Dtype)
    for i in range(3, WhitePlate):
        Table[i + WhitePlate] = zeros - Table[i]

    @staticmethod
    def errorSum(data, pattern):
        errorResult = 0
        for i in range(4):
            for j in range(4):
                err = pattern[i, j] - data[i, j]
                if err < 0:
                    errorResult -= err
                else:
                    errorResult += err
        return errorResult

    @classmethod
    def Estimate(cls, data):
        if data.shape != cls.Shape:
            raise Exception("Shape should be (4, 4)")
        da = data - 127   # 把 0-254 變 -127-0-127
        candiate = 0
        errorMin = cls.errorSum(da, cls.Table[0])
        for i in range(1, cls.TableSize):
            errorNow = cls.errorSum(da, cls.Table[i])
            if errorNow < errorMin:
                candiate = i
                errorMin = errorNow
        return candiate
