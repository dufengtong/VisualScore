#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
gui for key frame extraction and parameter tuning.
only test version.
"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
# from PyQt5.QtCore import QDir, QUrl, QThread, pyqtSignal, Qt
# from PyQt5.QtWidgets import *
# from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
import cv2
from QTimeLine.qtimeline import QTimeLine

class VideoThread_example(QtCore.QThread):
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                QtFormatImage = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QtGui.QImage.Format_RGB888)
                p = QtFormatImage.scaled(700, 500, QtCore.Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

class VideoThread(QtCore.QThread):
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                QtFormatImage = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QtGui.QImage.Format_RGB888)
                p = QtFormatImage.scaled(700, 500, QtCore.Qt.KeepAspectRatio)
                self.changePixmap.emit(p)


class VSMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setObjectName("MainWindow")
        self.resize(1100, 700)
        self.setWindowTitle('VisualScore')
        self.setWindowIcon(QtGui.QIcon('gui/eye.png'))

        # open video file from path
        self.add_open_video_toolbar()
        # start setting parameters
        self.add_set_params_toolbar()

        # video player window
        self.paramW = QtWidgets.QLabel('param_W')
        # self.timelineW = QtWidgets.QLabel('timeline_W')
        self.videoLabel =QtWidgets.QLabel('video_frame')
        self.videoLabel.setScaledContents(True)
        # self.label.resize(640, 480)

        self.timeline = QTimeLine(360, 10)

        palette1 = QtGui.QPalette()
        palette1.setColor(self.backgroundRole(), QtGui.QColor(255, 255, 255))  # 设置背景颜色
        self.setPalette(palette1)

        # set layout
        self.centralwidget = QtWidgets.QWidget(self)
        self.timeline.setFixedHeight(150)
        self.vLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.vLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(7)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_param = QtWidgets.QGridLayout()
        self.gridLayout_param.setContentsMargins(25, 25, 50, -1)
        self.gridLayout_param.setSpacing(15)
        self.gridLayout_param.setObjectName("gridLayout_param")
        self.paramLabel1 = QtWidgets.QLabel(self.centralwidget)
        self.paramLabel1.setObjectName("paramLabel1")
        self.gridLayout_param.addWidget(self.paramLabel1, 0, 0, 1, 1)
        self.paramLabel3 = QtWidgets.QLabel(self.centralwidget)
        self.paramLabel3.setObjectName("paramLabel3")
        self.gridLayout_param.addWidget(self.paramLabel3, 2, 0, 1, 1)
        self.paramLineEdit1 = QtWidgets.QLineEdit(self.centralwidget)
        self.paramLineEdit1.setObjectName("paramLineEdit1")
        self.gridLayout_param.addWidget(self.paramLineEdit1, 0, 1, 1, 1)
        self.paramLabel2 = QtWidgets.QLabel(self.centralwidget)
        self.paramLabel2.setObjectName("paramLabel2")
        self.gridLayout_param.addWidget(self.paramLabel2, 1, 0, 1, 1)
        self.paramLineEdit3 = QtWidgets.QLineEdit(self.centralwidget)
        self.paramLineEdit3.setObjectName("paramLineEdit3")
        self.gridLayout_param.addWidget(self.paramLineEdit3, 2, 1, 1, 1)
        self.paramLineEdit2 = QtWidgets.QLineEdit(self.centralwidget)
        self.paramLineEdit2.setObjectName("paramLineEdit2")
        self.gridLayout_param.addWidget(self.paramLineEdit2, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_param)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setObjectName("startButton")
        self.horizontalLayout_2.addStretch(1)
        self.horizontalLayout_2.addWidget(self.startButton)
        self.horizontalLayout_2.addStretch(1)
        self.horizontalLayout_2.setContentsMargins(-1,25,-1,-1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout_2,1)
        self.verticalLayout_2.addStretch(1)
        self.videoLabel = QtWidgets.QLabel(self.centralwidget)
        self.videoLabel.setObjectName("videoLabel")
        self.videoLabel.setScaledContents(True)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.addWidget(self.videoLabel)

        self.horizontalLayout.addLayout(self.verticalLayout_3,3)

        self.vLayout.addLayout(self.horizontalLayout)
        self.vLayout.addLayout(self.verticalLayout)
        self.verticalLayout.addWidget(self.timeline)

        self.setCentralWidget(self.centralwidget)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        # Set widget to contain window contents
        self.centralwidget.setLayout(self.vLayout)

        self.video_thread = VideoThread(self)
        self.video_thread.changePixmap.connect(self.setImage)
        self.video_thread.start()
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.paramLabel1.setText(_translate("MainWindow", "不舒适块数量"))
        self.paramLabel3.setText(_translate("MainWindow", "中心亮度差阈值"))
        self.paramLabel2.setText(_translate("MainWindow", "亮度差阈值"))
        self.startButton.setText(_translate("MainWindow", "开始"))
        self.videoLabel.setText(_translate("MainWindow", "TextLabel"))



    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QtWidgets.QMessageBox.Yes |
                                               QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):
        # move main window to the center of screen
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def openFile(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Video",
                                                  QtCore.QDir.homePath())

        if fileName != '':
            self.mediaPlayer.setMedia(QMediaContent(QtCore.QUrl.fromLocalFile(fileName)))

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

    def playVideo(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def add_open_video_toolbar(self):
        openAct = QtWidgets.QAction(QtGui.QIcon('gui/folder_open.png'), 'Open', self)
        openAct.triggered.connect(self.openFile)
        self.toolbar = self.addToolBar('Open')
        self.toolbar.addAction(openAct)

    def add_set_params_toolbar(self):
        startSetAct = QtWidgets.QAction(QtGui.QIcon('gui/start.png'), 'StartSet', self)
        startSetAct.triggered.connect(self.playVideo)
        self.toolbar = self.addToolBar('StartSet')
        self.toolbar.addAction(startSetAct)

    def setImage(self, image):
        image.scaled(self.width()*700/1000, self.height()*400/600, QtCore.Qt.KeepAspectRatio)
        self.videoLabel.setPixmap(QtGui.QPixmap.fromImage(image))

    # def resizeEvent(self, *args, **kwargs):




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex =VSMainWindow()
    ex.center()
    ex.show()
    sys.exit(app.exec_())