# -*- coding: utf-8 -*-

# coding by dft
# Form implementation generated from reading ui file 'D:\dft\program\VisualScore\untitled.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!
import PyQt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
from config import cfg
from tools import *
import datetime


class VideoThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def set_video_path(self, video_path):
        self.video_path = video_path
        self.uncomfort_block_num = None
        self.threshold = None
        self.center_thresh = None
        self.block_num = cfg.INTERNAL.BLOCK_NUM
        self.target_width = cfg.INTERNAL.IMAGE_W
        self.target_height = cfg.INTERNAL.IMAGE_H
        self.stopFlag = False

        video_name = self.video_path.split('/')[-1]
        now = datetime.datetime.now()
        uncomfort_root_dir = 'uncomfort_image_dir'
        if not os.path.exists(uncomfort_root_dir):
            os.mkdir(uncomfort_root_dir)
        self.uncomfort_frame_save_dir = '{}/{}_{}{}{}'.format(uncomfort_root_dir, video_name.split('.')[0], now.day, now.minute, now.second)
        self.txt_path = '{}/{}_{}{}{}.txt'.format(uncomfort_root_dir, video_name.split('.')[0], now.day, now.minute, now.second)
        if not os.path.exists(self.uncomfort_frame_save_dir):
            os.mkdir(self.uncomfort_frame_save_dir)

    def set_prarm(self, block_num, thresh, center_thresh):
        self.uncomfort_block_num = block_num
        self.threshold = thresh
        self.center_thresh = center_thresh
    #
    # def set_prameters(self):
    def __del__(self):
        self.stopFlag = True
        self.quit()
        self.wait()

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        result_lines = []

        if (self.uncomfort_block_num*self.threshold*self.center_thresh) == 0:
            self.uncomfort_block_num = cfg.INTERNAL.UNCOMFORT_BLOCK_NUM
            self.threshold = cfg.INTERNAL.LUMA_DIFF_THRESH
            self.center_thresh = cfg.INTERNAL.CENTER_LUMA_DIFF_THRESH

        for idx in range(video_length):
            if self.stopFlag == True:
                txt = open(self.txt_path, 'w')
                txt.writelines(result_lines)
                break
            if idx == 0:
                ret, last_frame = cap.read()
                last_frame_idx = 0
                continue
            ret, frame = cap.read()
            if idx % 2 == 0:
                continue

            uncomfort_block_num, block_luma_diff = videoEvalue(
                last_frame, frame, self.block_num, self.threshold, self.target_width, self.target_height)

            if (uncomfort_block_num >= self.uncomfort_block_num) or (
                    abs(block_luma_diff[1][1]) >= self.center_thresh):
               # print("frame {} and {} is uncomfort".format(idx - 1, idx))
               im_path = '%s\\%s.jpg' % (self.uncomfort_frame_save_dir, str(idx))
               cv2.imwrite(im_path, frame)
               im_path = '%s\\%s.jpg' % (self.uncomfort_frame_save_dir, str(last_frame_idx))
               cv2.imwrite(im_path, last_frame)

               line = [last_frame_idx, idx, uncomfort_block_num]
               for diff in block_luma_diff: line.append(diff)
               line.append('\n')
               str_line = ' '.join(str(e) for e in line)
               result_lines.append(str_line)

            last_frame = frame
            last_frame_idx = idx
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                QtFormatImage = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
                p = QtFormatImage.scaled(600, 400, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)
        txt = open(self.txt_path, 'w')
        txt.writelines(result_lines)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.mainWindow = MainWindow
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1272, 800)
        MainWindow.setWindowIcon(QIcon('%s/gui/eye.png'%self.current_dir))

        palette1 = QPalette()
        palette1.setColor(MainWindow.backgroundRole(), QColor(255, 255, 255))  # 设置背景颜色
        MainWindow.setPalette(palette1)

        # open video file from path
        self.add_open_video_toolbar(MainWindow)
        # start setting parameters
        self.add_set_params_toolbar(MainWindow)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.paramLayout = QHBoxLayout()
        self.paramLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.paramLayout.setContentsMargins(100, -1, 100, -1)
        self.paramLayout.setSpacing(100)
        self.paramLayout.setObjectName("paramLayout")
        self.paramLayout_1 = QHBoxLayout()
        self.paramLayout_1.setContentsMargins(-1, -1, 50, -1)
        self.paramLayout_1.setSpacing(20)
        self.paramLayout_1.setObjectName("paramLayout_1")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.paramLayout_1.addWidget(self.label)
        self.lineEdit = QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.paramLayout_1.addWidget(self.lineEdit)
        self.paramLayout.addLayout(self.paramLayout_1)
        self.paramLayout_2 = QHBoxLayout()
        self.paramLayout_2.setContentsMargins(-1, -1, 50, -1)
        self.paramLayout_2.setSpacing(20)
        self.paramLayout_2.setObjectName("paramLayout_2")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.paramLayout_2.addWidget(self.label_2)
        self.lineEdit_2 = QLineEdit(self.centralwidget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.paramLayout_2.addWidget(self.lineEdit_2)
        self.paramLayout.addLayout(self.paramLayout_2)
        self.paramLayout_3 = QHBoxLayout()
        self.paramLayout_3.setContentsMargins(-1, -1, 50, -1)
        self.paramLayout_3.setSpacing(20)
        self.paramLayout_3.setObjectName("paramLayout_3")
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.paramLayout_3.addWidget(self.label_3)
        self.lineEdit_3 = QLineEdit(self.centralwidget)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.paramLayout_3.addWidget(self.lineEdit_3)
        self.paramLayout.addLayout(self.paramLayout_3)
        self.verticalLayout.addLayout(self.paramLayout)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(50)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName("label_4")
        self.label_4.setScaledContents(True)
        self.horizontalLayout_4.addWidget(self.label_4)
        self.label_5 = QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.label_5.setScaledContents(True)
        self.horizontalLayout_4.addWidget(self.label_5)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setContentsMargins(-1, 20, -1, 20)
        self.horizontalLayout_5.setSpacing(50)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.tableView = QTableView(self.centralwidget)
        self.tableView.setMaximumSize(QSize(100, 100))
        self.tableView.setBaseSize(QSize(0, 0))
        self.tableView.setObjectName("tableView")
        self.horizontalLayout_5.addWidget(self.tableView)
        self.tableView_2 = QTableView(self.centralwidget)
        self.tableView_2.setMaximumSize(QSize(100, 100))
        self.tableView_2.setObjectName("tableView_2")
        self.horizontalLayout_5.addWidget(self.tableView_2)
        self.tableView_3 = QTableView(self.centralwidget)
        self.tableView_3.setMaximumSize(QSize(100, 100))
        self.tableView_3.setObjectName("tableView_3")
        self.horizontalLayout_5.addWidget(self.tableView_3)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.graphicsView = QGraphicsView(self.centralwidget)
        self.graphicsView.setMaximumSize(QSize(16777215, 100))
        self.graphicsView.setObjectName("graphicsView")
        # self.timeline = VStimelineWidget()
        # self.timeline = VStimelineWidget()
        # self.timelineScene = QGraphicsScene()
        # self.timelineScene.addWidget(self.timeline)
        # self.graphicsView.setScene(self.timelineScene)
        self.verticalLayout.addWidget(self.graphicsView)
        self.verticalLayout.setStretch(1, 1)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 1000, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.video_thread = VideoThread(MainWindow)
        self.video_thread.changePixmap.connect(self.setImage)
        self.fileName = None


        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)
        self.label_4.setText("")
        self.label_5.setText("")
        MainWindow.setWindowTitle('不舒适帧检测器')

    def setImage(self, image):
        # image.scaled(self.width()*700/1000, self.height()*400/600, Qt.KeepAspectRatio)
        self.label_4.setPixmap(QPixmap.fromImage(image))
        self.label_5.setPixmap(QPixmap.fromImage(image))


    def add_open_video_toolbar(self,MainWindow):
        openAct = QAction(QIcon('%s/gui/folder_open.png'%self.current_dir), 'Open', MainWindow)
        openAct.triggered.connect(self.openFile)
        self.toolbar = MainWindow.addToolBar('Open')
        self.toolbar.addAction(openAct)

    def openFile(self):
        if self.video_thread.isRunning():
            self.video_thread.__del__()

        fileName, _ = QFileDialog.getOpenFileName(self.mainWindow, "Open Video",
                                                  QDir.homePath())
        if fileName != '' :
            self.fileName = fileName
            self.video_thread.set_video_path(fileName)



    def add_set_params_toolbar(self,MainWindow):
        startSetAct = QAction(QIcon('%s/gui/start.png'%self.current_dir), 'StartSet', MainWindow)
        startSetAct.triggered.connect(self.setParameter)
        self.toolbar = MainWindow.addToolBar('StartSet')
        self.toolbar.addAction(startSetAct)

    def setParameter(self):
        if self.fileName == None:
            QMessageBox.warning(self.mainWindow, "提示", "您还没有选择视频！")
        else:
            uncomfort_block_num = self.lineEdit.text()
            center_luma_thresh = self.lineEdit_2.text()
            luma_diff_thresh = self.lineEdit_3.text()
            if (len(uncomfort_block_num)*len(center_luma_thresh)*len(luma_diff_thresh) == 0):
                QMessageBox.warning(self.mainWindow, "提示", "您还没有输入参数！")
            else:
                self.video_thread.set_prarm(int(uncomfort_block_num), float(center_luma_thresh), float(luma_diff_thresh))
                self.video_thread.start()

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "不舒适块数量"))
        self.label_2.setText(_translate("MainWindow", "中心亮度差阈值"))
        self.label_3.setText(_translate("MainWindow", "亮度差阈值"))
        self.label_4.setText(_translate("MainWindow", "TextLabel"))
        self.label_5.setText(_translate("MainWindow", "TextLabel"))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

