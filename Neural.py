# -*- coding: utf-8 -*-
# @Time    : 2018/9/13 下午 04:10
# @Author  : AlexJean
import torch
import torch.nn as nn
import torch.nn.init as init


class Net(nn.Module):

    LearningRate = 0.00002

    def __init__(self, classNo):
        super(Net, self).__init__()
        # Conv2d input形式為(batchN,C_in,H,W)
        # outout 為(batchN,C_out,H,W)
        self.conv1 = nn.Conv2d(1, 128, (5, 5), stride=(1, 1), padding=(2, 2))
        self.conv2 = nn.Conv2d(128, 128, (3, 3), (1, 1), (1, 1))
        self.conv3 = nn.Conv2d(128, 64, (3, 3), (1, 1), (1, 1))
        self.conv4 = nn.Conv2d(64,  classNo, (3, 3), (1, 1), (1, 1))
        self._initialize_weights()

    def forward(self, x):
        x = torch.tanh(self.conv1(x))
        x = torch.tanh(self.conv2(x))
        x = torch.tanh(self.conv3(x))
        x = self.conv4(x)            # [batch, 5, H, W]
        return x

    def _initialize_weights(self):
        init.xavier_normal_(self.conv1.weight, init.calculate_gain('tanh'))
        init.xavier_normal_(self.conv2.weight, init.calculate_gain('tanh'))
        init.xavier_normal_(self.conv3.weight, init.calculate_gain('tanh'))
        init.xavier_normal_(self.conv4.weight)
