# -*- coding: utf-8 -*-
# @Time    : 2018/9/13 下午 04:10
# @Author  : AlexJean
import torch.nn as nn
import torch.nn.functional as F


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 64, (5, 5), (1, 1), (2, 2))
        self.conv2 = nn.Conv2d(64, 64, (3, 3), (1, 1), (1, 1))
        self.conv3 = nn.Conv2d(64, 64, (3, 3), (1, 1), (1, 1))
        self.conv4 = nn.Conv2d(64, 16, (3, 3), (1, 1), (1, 1))

    def forward(self, x):
        x = F.tanh(self.conv1(x))
        x = F.tanh(self.conv2(x))
        x = F.tanh(self.conv3(x))
        x = F.softmax(self.conv4(x))
        return x
