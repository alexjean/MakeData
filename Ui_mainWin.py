# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWin.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1081, 829)
        Dialog.setWindowTitle("Make trainData for diffLayer lineDetector")
        self.btnLine = QtWidgets.QPushButton(Dialog)
        self.btnLine.setGeometry(QtCore.QRect(20, 540, 75, 23))
        self.btnLine.setObjectName("btnLine")
        self.view = QtWidgets.QGraphicsView(Dialog)
        self.view.setGeometry(QtCore.QRect(10, 10, 321, 231))
        self.view.setObjectName("view")
        self.btnClear = QtWidgets.QPushButton(Dialog)
        self.btnClear.setGeometry(QtCore.QRect(20, 570, 75, 23))
        self.btnClear.setObjectName("btnClear")
        self.viewLarge = QtWidgets.QGraphicsView(Dialog)
        self.viewLarge.setGeometry(QtCore.QRect(340, 10, 731, 811))
        self.viewLarge.setObjectName("viewLarge")
        self.view1 = QtWidgets.QGraphicsView(Dialog)
        self.view1.setGeometry(QtCore.QRect(10, 280, 321, 231))
        self.view1.setObjectName("view1")
        self.btnSave = QtWidgets.QPushButton(Dialog)
        self.btnSave.setGeometry(QtCore.QRect(20, 600, 75, 23))
        self.btnSave.setObjectName("btnSave")
        self.leTrainFileName = QtWidgets.QLineEdit(Dialog)
        self.leTrainFileName.setGeometry(QtCore.QRect(20, 630, 71, 20))
        self.leTrainFileName.setObjectName("leTrainFileName")
        self.sboxTrainFileName = QtWidgets.QSpinBox(Dialog)
        self.sboxTrainFileName.setGeometry(QtCore.QRect(110, 630, 51, 22))
        self.sboxTrainFileName.setMaximum(9999)
        self.sboxTrainFileName.setObjectName("sboxTrainFileName")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(100, 630, 21, 21))
        self.label.setObjectName("label")
        self.btnLoad = QtWidgets.QPushButton(Dialog)
        self.btnLoad.setGeometry(QtCore.QRect(20, 660, 75, 23))
        self.btnLoad.setObjectName("btnLoad")
        self.btnCalcTrainLabel = QtWidgets.QPushButton(Dialog)
        self.btnCalcTrainLabel.setGeometry(QtCore.QRect(110, 540, 81, 23))
        self.btnCalcTrainLabel.setObjectName("btnCalcTrainLabel")
        self.view.raise_()
        self.viewLarge.raise_()
        self.btnClear.raise_()
        self.btnLine.raise_()
        self.view1.raise_()
        self.btnSave.raise_()
        self.leTrainFileName.raise_()
        self.sboxTrainFileName.raise_()
        self.label.raise_()
        self.btnLoad.raise_()
        self.btnCalcTrainLabel.raise_()

        self.retranslateUi(Dialog)
        self.btnLine.clicked.connect(Dialog.doLine)
        self.btnClear.clicked.connect(Dialog.clearWorld)
        self.btnSave.clicked.connect(Dialog.saveTrainData)
        self.btnLoad.clicked.connect(Dialog.loadData)
        self.btnCalcTrainLabel.clicked.connect(Dialog.calcTrainLabel)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.btnClear, self.btnLine)
        Dialog.setTabOrder(self.btnLine, self.view)
        Dialog.setTabOrder(self.view, self.viewLarge)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        self.btnLine.setText(_translate("Dialog", "Do Line"))
        self.btnClear.setText(_translate("Dialog", "Clear"))
        self.btnSave.setText(_translate("Dialog", "Save"))
        self.leTrainFileName.setText(_translate("Dialog", "EdgeTrain"))
        self.label.setText(_translate("Dialog", "_"))
        self.btnLoad.setText(_translate("Dialog", "Load"))
        self.btnCalcTrainLabel.setText(_translate("Dialog", "CalcTrainLabel"))

