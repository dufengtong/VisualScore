# -*- coding: utf-8 -*-

# coding by dft
# Form implementation generated from reading ui file 'D:\dft\program\VisualScore\untitled.ui'
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
from config import cfg
from tools import *
import datetime
from VStimeline import timelineW

class VideoThread(QThread):
    changePixmap = pyqtSignal(QImage)
    returnUncomfortFrameIdx = pyqtSignal(int, int)
    resetVideoLength = pyqtSignal(float)
    setCurrentTime = pyqtSignal(float, float)
    finishSignal = pyqtSignal(bool)
    def set_video_path(self, video_path):
        self.video_path = video_path
        self.uncomfort_block_num = None
        self.threshold = None
        self.center_thresh = None
        self.color_thresh = None
        self.color_uncomfort_block_num = None
        self.color_threshold = None
        self.color_center_thresh = None
        self.block_num = cfg.INTERNAL.BLOCK_NUM
        self.target_width = cfg.INTERNAL.IMAGE_W
        self.target_height = cfg.INTERNAL.IMAGE_H
        self.stopFlag = False
        self.pause = False
        self.mode_idx = None

        video_name = self.video_path.split('/')[-1]
        now = datetime.datetime.now()
        uncomfort_root_dir = 'uncomfort_image_dir'
        if not os.path.exists(uncomfort_root_dir):
            os.mkdir(uncomfort_root_dir)
        self.uncomfort_frame_save_dir = '{}/{}_{}{}{}'.format(uncomfort_root_dir, video_name.split('.')[0], now.day, now.minute, now.second)
        self.txt_path = '{}/{}_{}{}{}.txt'.format(uncomfort_root_dir, video_name.split('.')[0], now.day, now.minute, now.second)
        if not os.path.exists(self.uncomfort_frame_save_dir):
            os.mkdir(self.uncomfort_frame_save_dir)

    def set_luma_prarm(self, block_num, center_thresh, thresh):
        self.uncomfort_block_num = block_num
        self.threshold = thresh
        self.center_thresh = center_thresh

    def set_color_prarm(self, block_num, center_thresh, thresh):
        self.color_uncomfort_block_num = block_num
        self.color_threshold = thresh
        self.color_center_thresh = center_thresh

    def set_3block_mode_luma_param(self,top,center,bottom):
        self.top_luma_thresh = top
        self.center_luma_thresh = center
        self.bottom_luma_thresh = bottom
        
    def set_3block_mode_color_param(self,top,center,bottom):
        self.top_color_thresh = top
        self.center_color_thresh = center
        self.bottom_color_thresh = bottom

    def set_mode(self, index):
        # idx=0 for 9 block mode, 1 for 3 block mode
        self.mode_idx = index

    def set_param_default_value(self):
        if self.mode_idx == 0:
            if (self.uncomfort_block_num*self.threshold*self.center_thresh) == 0:
                self.uncomfort_block_num = cfg.INTERNAL.UNCOMFORT_BLOCK_NUM
                self.threshold = cfg.INTERNAL.LUMA_DIFF_THRESH
                self.center_thresh = cfg.INTERNAL.CENTER_LUMA_DIFF_THRESH
            if (self.color_threshold*self.color_uncomfort_block_num*self.color_center_thresh) == 0:
                self.color_uncomfort_block_num = cfg.INTERNAL.COLOR_UNCOMFORT_BLOCK_NUM
                self.color_threshold = cfg.INTERNAL.COLOR_DIFF_THRESH
                self.color_center_thresh = cfg.INTERNAL.CENTER_COLOR_DIFF_THRESH
        if self.mode_idx == 1:
            if (self.top_luma_thresh*self.center_luma_thresh*self.bottom_luma_thresh) == 0:
                self.top_luma_thresh = cfg.INTERNAL.TOP_LUMA_THRESH
                self.center_luma_thresh = cfg.INTERNAL.CENTER_LUMA_THRESH
                self.bottom_luma_thresh = cfg.INTERNAL.BOTTOM_LUMA_THRESH
            if (self.top_color_thresh*self.center_color_thresh*self.bottom_color_thresh) == 0:
                self.top_color_thresh = cfg.INTERNAL.TOP_COLOR_THRESH
                self.center_color_thresh = cfg.INTERNAL.CENTER_COLOR_THRESH
                self.bottom_color_thresh = cfg.INTERNAL.BOTTOM_COLOR_THRESH

    # def set_prameters(self):
    def __del__(self):
        self.stopFlag = True
        self.quit()
        self.wait()

    def run(self):
        self.stopFlag = False
        cap = cv2.VideoCapture(str(self.video_path))
        fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
        is_uncomfort = False
        video_length = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        self.resetVideoLength.emit(video_length/fps)

        result_lines = []

        # when parameters are not given, use default values.
        self.set_param_default_value()

        if self.mode_idx == 1:
            threshold_array = np.array([self.top_luma_thresh, self.center_luma_thresh, self.bottom_luma_thresh,
                          self.top_color_thresh, self.center_color_thresh, self.bottom_color_thresh])
            self.threshold_array = threshold_array

        for idx in range(video_length):
            while self.pause == True:
                self.sleep(1)
            if self.stopFlag == True:
                txt = open(self.txt_path, 'w')
                txt.writelines(result_lines)
                break
            if idx == 0:
                ret, last_frame = cap.read()
                last_frame_idx = 0
                continue
            m, s = divmod(idx/float(fps), 60)
            self.setCurrentTime.emit(m, s)
            ret, frame = cap.read()
            # if idx % 2 == 0:
            #     continue
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                QtFormatImage = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
                p = QtFormatImage.scaled(600, 400, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

            if self.mode_idx == 0:
                uncomfort_block_num, block_luma_diff = videoEvalue(
                    last_frame, frame, self.block_num, self.threshold, self.target_width, self.target_height)
                color_uncomfort_block_num, block_color_diff = videoColorEvalue(last_frame, frame, self.block_num, self.color_threshold)

                if (uncomfort_block_num >= self.uncomfort_block_num) or \
                        (abs(block_luma_diff[1][1]) >= self.center_thresh) or \
                        (color_uncomfort_block_num >= self.color_uncomfort_block_num) or \
                        (abs(block_color_diff[1][1]) >= self.color_center_thresh):
                    is_uncomfort = True
            else:
                uncomfort_block_num, block_luma_diff, block_color_diff = video3BlockEvalue(last_frame, frame, threshold_array, self.target_width, self.target_height)
                if uncomfort_block_num > 0:
                    is_uncomfort = True

            if is_uncomfort == True:
                im_path = '%s\\%s.jpg' % (self.uncomfort_frame_save_dir, str(idx))
                cv2.imwrite(im_path, frame)
                im_path = '%s\\%s.jpg' % (self.uncomfort_frame_save_dir, str(last_frame_idx))
                cv2.imwrite(im_path, last_frame)

                line = [last_frame_idx, idx, uncomfort_block_num]
                for diff in block_luma_diff: line.append(diff)
                for diff in block_color_diff: line.append(diff)
                line.append('\n')
                str_line = ' '.join(str(e) for e in line)
                result_lines.append(str_line)
                self.returnUncomfortFrameIdx.emit(idx, fps) # idx is the idx of the latter frame

            is_uncomfort = False
            last_frame = frame
            last_frame_idx = idx

        self.finishSignal.emit(True)
        self.stopFlag = True
        txt = open(self.txt_path, 'w')
        txt.writelines(result_lines)

class Window(QMainWindow):
    resized = pyqtSignal(QSize)
    def __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.resized.connect(self.ui.resizeTimeline)

    def resizeEvent(self, event):
        self.resized.emit(self.size())
        return super(Window, self).resizeEvent(event)

    def closeEvent(self, *args, **kwargs):
        self.ui.video_thread.pause = False
        self.ui.video_thread.stopFlag = True
        self.ui.video_thread.quit()
        return super(Window, self).closeEvent(*args, **kwargs)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.mainWindow = MainWindow
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1272, 1000)
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
        
        # main vertical layout
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        # horizontal layout for mode combobox and param vertical layout
        self.horizontalLayout_1 = QHBoxLayout()
        self.horizontalLayout_1.setObjectName('horizontalLayout_1')

        # add combobox for selecting mode
        self.verticalLayout_combobox = QVBoxLayout()
        self.verticalLayout_combobox.setContentsMargins(50,0,0,0)
        self.combobox_mode = QComboBox()
        self.combobox_mode.addItem("9 block mode")
        self.combobox_mode.addItem("3 block mode")
        self.combobox_mode.currentIndexChanged.connect(self.changeMode)
        self.verticalLayout_combobox.addWidget(self.combobox_mode)
        self.horizontalLayout_1.addLayout(self.verticalLayout_combobox)

        # parameter layout
        self.verticalLayout_param = QVBoxLayout()
        self.verticalLayout_param.setObjectName('verticalLayout_param')
        
        # parameter layout for luminance
        self.setup_luma_param_layout()
        
        # parameter layout for color
        self.setup_color_param_layout()

        # add two parameter layout to param vertical layout
        self.verticalLayout_param.addLayout(self.paramLayout)
        self.verticalLayout_param.addLayout(self.paramColorLayout)

        self.horizontalLayout_1.addLayout(self.verticalLayout_param)
        self.verticalLayout.addLayout(self.horizontalLayout_1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(50)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_lastFrame = QLabel(self.centralwidget)
        self.label_lastFrame.setObjectName("label_lastFrame")
        self.label_lastFrame.setScaledContents(True)
        self.horizontalLayout_4.addWidget(self.label_lastFrame)
        self.label_nextFrame = QLabel(self.centralwidget)
        self.label_nextFrame.setObjectName("label_nextFrame")
        self.label_nextFrame.setScaledContents(True)
        self.horizontalLayout_4.addWidget(self.label_nextFrame)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setContentsMargins(-1, 20, -1, 20)
        self.horizontalLayout_5.setSpacing(50)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.table_lastFrameMat = QTableWidget(self.centralwidget)
        self.table_lastFrameMat.setMaximumSize(QSize(198, 99))
        self.table_lastFrameMat.setBaseSize(QSize(0, 0))
        self.table_lastFrameMat.setObjectName("table_lastFrameMat")
        self.horizontalLayout_5.addWidget(self.table_lastFrameMat)
        self.table_frameMatDiff = QTableWidget(self.centralwidget)
        self.table_frameMatDiff.setMaximumSize(QSize(198, 99))
        self.table_frameMatDiff.setObjectName("table_frameMatDiff")
        self.horizontalLayout_5.addWidget(self.table_frameMatDiff)
        self.table_frameMatColorDiff = QTableWidget(self.centralwidget)
        self.table_frameMatColorDiff.setMaximumSize(QSize(198, 99))
        self.table_frameMatColorDiff.setObjectName("table_frameMatColorDiff")
        self.horizontalLayout_5.addWidget(self.table_frameMatColorDiff)
        self.table_nextFrameMat = QTableWidget(self.centralwidget)
        self.table_nextFrameMat.setMaximumSize(QSize(198, 99))
        self.table_nextFrameMat.setObjectName("table_nextFrameMat")
        self.horizontalLayout_5.addWidget(self.table_nextFrameMat)

        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setContentsMargins(10, 0, 20, 0)
        self.horizontalLayout_6.setAlignment(Qt.AlignCenter)
        self.horizontalLayout_6.setSpacing(260)

        self.label_lastFrameLuma = QLabel(self.centralwidget)
        self.label_lastFrameLuma.setObjectName("label_lastFrameLuma")
        self.label_lastFrameLuma.setText("last frame luminance")
        self.horizontalLayout_6.addWidget(self.label_lastFrameLuma)

        self.label_lumaDiff = QLabel(self.centralwidget)
        self.label_lumaDiff.setObjectName("label_lumaDiff")
        self.label_lumaDiff.setText("difference of luminance")
        self.horizontalLayout_6.addWidget(self.label_lumaDiff)

        self.label_colorDiff = QLabel(self.centralwidget)
        self.label_colorDiff.setObjectName("label_colorDiff")
        self.label_colorDiff.setText("difference of color")
        self.horizontalLayout_6.addWidget(self.label_colorDiff)

        self.label_nextFrameLuma = QLabel(self.centralwidget)
        self.label_nextFrameLuma.setObjectName("label_nextFrameLuma")
        self.label_nextFrameLuma.setText("next frame luminance")
        self.horizontalLayout_6.addWidget(self.label_nextFrameLuma)

        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.timeline = timelineW()
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.timeline)
        # self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setMaximumHeight(200)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalLayout.addWidget(self.scrollArea)

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
        self.video_thread.returnUncomfortFrameIdx.connect(self.timeline.addUncomfortPoint)
        self.video_thread.resetVideoLength.connect(self.timeline.resetVideoLength)
        self.fileName = None
        self.isProcessing = False
        self.timeline.setUncomfortFrames.connect(self.setUncomfortPixelmaps)
        self.video_thread.setCurrentTime.connect(self.showTime)
        self.video_thread.finishSignal.connect(self.handleFinishSignal)


        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)
        self.label_lastFrame.setText("")
        self.label_nextFrame.setText("")

        self.current_mode = 0
        
    def setup_luma_param_layout(self):
        self.paramLayout = QHBoxLayout()
        self.paramLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.paramLayout.setContentsMargins(100, -1, 100, -1)
        self.paramLayout.setSpacing(100)
        self.paramLayout.setObjectName("paramLayout")
        self.paramLayout_uncomforBlockNum = QHBoxLayout()
        self.paramLayout_uncomforBlockNum.setContentsMargins(-1, -1, 50, -1)
        self.paramLayout_uncomforBlockNum.setSpacing(20)
        self.paramLayout_uncomforBlockNum.setObjectName("paramLayout_uncomforBlockNum")
        self.label_uncomfortBlockNum = QLabel(self.centralwidget)
        self.label_uncomfortBlockNum.setObjectName("label_uncomfortBlockNum")
        self.paramLayout_uncomforBlockNum.addWidget(self.label_uncomfortBlockNum)
        self.lineEdit_uncomfortBlockNum = QLineEdit(self.centralwidget)
        self.lineEdit_uncomfortBlockNum.setObjectName("lineEdit_uncomfortBlockNum")
        self.paramLayout_uncomforBlockNum.addWidget(self.lineEdit_uncomfortBlockNum)
        self.paramLayout.addLayout(self.paramLayout_uncomforBlockNum)
        self.paramLayout_centerThresh = QHBoxLayout()
        self.paramLayout_centerThresh.setContentsMargins(-1, -1, 50, -1)
        self.paramLayout_centerThresh.setSpacing(20)
        self.paramLayout_centerThresh.setObjectName("paramLayout_centerThresh")
        self.label_centerThresh = QLabel(self.centralwidget)
        self.label_centerThresh.setObjectName("label_centerThresh")
        self.paramLayout_centerThresh.addWidget(self.label_centerThresh)
        self.lineEdit_centerThresh = QLineEdit(self.centralwidget)
        self.lineEdit_centerThresh.setObjectName("lineEdit_centerThresh")
        self.paramLayout_centerThresh.addWidget(self.lineEdit_centerThresh)
        self.paramLayout.addLayout(self.paramLayout_centerThresh)
        self.paramLayout_thresh = QHBoxLayout()
        self.paramLayout_thresh.setContentsMargins(-1, -1, 50, -1)
        self.paramLayout_thresh.setSpacing(20)
        self.paramLayout_thresh.setObjectName("paramLayout_thresh")
        self.label_thresh = QLabel(self.centralwidget)
        self.label_thresh.setObjectName("label_thresh")
        self.paramLayout_thresh.addWidget(self.label_thresh)
        self.lineEdit_thresh = QLineEdit(self.centralwidget)
        self.lineEdit_thresh.setObjectName("lineEdit_thresh")
        self.paramLayout_thresh.addWidget(self.lineEdit_thresh)
        self.paramLayout.addLayout(self.paramLayout_thresh)
        # self.verticalLayout.addLayout(self.paramLayout)

    def setup_color_param_layout(self):
        self.paramColorLayout = QHBoxLayout()
        self.paramColorLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.paramColorLayout.setContentsMargins(100, -1, 100, -1)
        self.paramColorLayout.setSpacing(100)
        self.paramColorLayout.setObjectName("paramColorLayout")
        self.paramColorLayout_uncomforBlockNum = QHBoxLayout()
        self.paramColorLayout_uncomforBlockNum.setContentsMargins(-1, -1, 50, -1)
        self.paramColorLayout_uncomforBlockNum.setSpacing(20)
        self.paramColorLayout_uncomforBlockNum.setObjectName("paramColorLayout_uncomforBlockNum")
        self.label_colorUncomfortBlockNum = QLabel(self.centralwidget)
        self.label_colorUncomfortBlockNum.setObjectName("label_colorUncomfortBlockNum")
        self.paramColorLayout_uncomforBlockNum.addWidget(self.label_colorUncomfortBlockNum)
        self.lineEdit_colorUncomfortBlockNum = QLineEdit(self.centralwidget)
        self.lineEdit_colorUncomfortBlockNum.setObjectName("lineEdit_colorUncomfortBlockNum")
        self.paramColorLayout_uncomforBlockNum.addWidget(self.lineEdit_colorUncomfortBlockNum)
        self.paramColorLayout.addLayout(self.paramColorLayout_uncomforBlockNum)
        self.paramColorLayout_centerThresh = QHBoxLayout()
        self.paramColorLayout_centerThresh.setContentsMargins(-1, -1, 50, -1)
        self.paramColorLayout_centerThresh.setSpacing(20)
        self.paramColorLayout_centerThresh.setObjectName("paramColorLayout_centerThresh")
        self.label_colorCenterThresh = QLabel(self.centralwidget)
        self.label_colorCenterThresh.setObjectName("label_colorCenterThresh")
        self.paramColorLayout_centerThresh.addWidget(self.label_colorCenterThresh)
        self.lineEdit_colorCenterThresh = QLineEdit(self.centralwidget)
        self.lineEdit_colorCenterThresh.setObjectName("lineEdit_colorCenterThresh")
        self.paramColorLayout_centerThresh.addWidget(self.lineEdit_colorCenterThresh)
        self.paramColorLayout.addLayout(self.paramColorLayout_centerThresh)
        self.paramColorLayout_thresh = QHBoxLayout()
        self.paramColorLayout_thresh.setContentsMargins(-1, -1, 50, -1)
        self.paramColorLayout_thresh.setSpacing(20)
        self.paramColorLayout_thresh.setObjectName("paramColorLayout_thresh")
        self.label_colorThresh = QLabel(self.centralwidget)
        self.label_colorThresh.setObjectName("label_colorThresh")
        self.paramColorLayout_thresh.addWidget(self.label_colorThresh)
        self.lineEdit_colorThresh = QLineEdit(self.centralwidget)
        self.lineEdit_colorThresh.setObjectName("lineEdit_colorThresh")
        self.paramColorLayout_thresh.addWidget(self.lineEdit_colorThresh)
        self.paramColorLayout.addLayout(self.paramColorLayout_thresh)

    def changeMode(self,i):
        if self.combobox_mode.currentIndex() == 0:
            self.label_uncomfortBlockNum.setText("luminance uncomfortable block number threshold")
            self.label_centerThresh.setText("center luminance difference threshold")
            self.label_thresh.setText("luminance difference threshold")
            self.label_colorUncomfortBlockNum.setText("color uncomfortable block number threshold    ")
            self.label_colorCenterThresh.setText("center color difference threshold    ")
            self.label_colorThresh.setText("color difference threshold    ")
        else:
            self.label_uncomfortBlockNum.setText("top luminance difference threshold")
            self.label_centerThresh.setText("center luminance difference threshold")
            self.label_thresh.setText("bottom luminance difference threshold")
            self.label_colorUncomfortBlockNum.setText("top color difference threshold    ")
            self.label_colorCenterThresh.setText("center color difference threshold    ")
            self.label_colorThresh.setText("bottom color difference threshold    ")


    def showMatrix(self, matrix, tableView):
        tableView.horizontalHeader().hide()
        tableView.verticalHeader().hide()
        tableView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tableView.setRowCount(len(matrix))

        if self.current_mode == 0:
            tableView.setColumnCount(len(matrix[0]))
            for i, row in enumerate(matrix):
                tableView.setColumnWidth(i, 66)
                tableView.setRowHeight(i, 33)
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(int(val)))
                    item.setTextAlignment(Qt.AlignCenter)
                    tableView.setItem(i, j, item)
        else:
            tableView.setColumnCount(1)
            for i, val in enumerate(matrix):
                tableView.setColumnWidth(i, 66 * 3)
                tableView.setRowHeight(i, 33)
                item = QTableWidgetItem(str(int(val)))
                item.setTextAlignment(Qt.AlignCenter)
                tableView.setItem(i, 0, item)

    def handleFinishSignal(self, isFinished):
        if isFinished:
            self.isProcessing = False
            self.video_thread.__del__()
            self.startSetAct.setIcon(QIcon('%s/gui/start.png' % self.current_dir))

    def showTime(self, minute, second):
        self.statusbar.showMessage('time %.2d:%.2d'%(minute, second))

    def frameToQimage(self, frame):
        rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        QtFormatImage = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
        return QtFormatImage.scaled(600, 400, Qt.KeepAspectRatio)

    def setUncomfortPixelmaps(self, frame_idx):
        if (self.video_thread.pause == True) or (self.video_thread.stopFlag == True):
            frame1_path = "%s//%s.jpg"%(self.video_thread.uncomfort_frame_save_dir, str(frame_idx-1))
            frame2_path = "%s//%s.jpg"%(self.video_thread.uncomfort_frame_save_dir, str(frame_idx))
            if os.path.exists(frame1_path) and os.path.exists(frame2_path):
                frame1 = cv2.imread(frame1_path)
                frame2 = cv2.imread(frame2_path)
                image1 = self.frameToQimage(frame1)
                image2 = self.frameToQimage(frame2)
                self.label_lastFrame.setPixmap(QPixmap.fromImage(image1))
                self.label_nextFrame.setPixmap(QPixmap.fromImage(image2))
                self.statusbar.showMessage('Frame %d and %d'%(frame_idx-1, frame_idx))

                if self.current_mode == 0:
                    luma1 = luminance(frame1, self.video_thread.target_width, self.video_thread.target_height)
                    luma2 = luminance(frame2, self.video_thread.target_width, self.video_thread.target_height)
                    block_luma1 = averageLuma(luma1, self.video_thread.block_num)
                    block_luma2 = averageLuma(luma2, self.video_thread.block_num)
                    block_luma_diff = lumaDifference(block_luma1, block_luma2)
                    self.showMatrix(block_luma1, self.table_lastFrameMat)
                    self.showMatrix(block_luma2, self.table_nextFrameMat)
                    self.showMatrix(block_luma_diff, self.table_frameMatDiff)

                    _, block_color_delta = videoColorEvalue(frame1,frame2,self.video_thread.block_num,self.video_thread.color_threshold)
                    self.showMatrix(block_color_delta, self.table_frameMatColorDiff)
                else:
                    luma1 = luminance(frame1, self.video_thread.target_width, self.video_thread.target_height)
                    luma2 = luminance(frame2, self.video_thread.target_width, self.video_thread.target_height)
                    block_luma1 = averageLuma3Block(luma1, 3)
                    block_luma2 = averageLuma3Block(luma2, 3)
                    _, block_luma_diff, block_color_diff = video3BlockEvalue(frame1,frame2,self.video_thread.threshold_array,self.video_thread.target_width,self.video_thread.target_height)
                    self.showMatrix(block_luma1, self.table_lastFrameMat)
                    self.showMatrix(block_luma2, self.table_nextFrameMat)
                    self.showMatrix(block_luma_diff, self.table_frameMatDiff)
                    self.showMatrix(block_color_diff, self.table_frameMatColorDiff)
            else:
                QMessageBox.warning(self.mainWindow, "Message", "Please don't delete uncomfort image directory when processing the video!")



    def resizeTimeline(self, areaSize):
        self.timeline.plot_timeline(areaSize)

    def setImage(self, image):
        # image.scaled(self.width()*700/1000, self.height()*400/600, Qt.KeepAspectRatio)
        self.label_lastFrame.setPixmap(QPixmap.fromImage(image))
        self.label_nextFrame.setPixmap(QPixmap.fromImage(image))

    def add_open_video_toolbar(self,MainWindow):
        openAct = QAction(QIcon('%s/gui/folder_open.png'%self.current_dir), 'Open', MainWindow)
        openAct.triggered.connect(self.openFile)
        self.toolbar = MainWindow.addToolBar('Open')
        self.toolbar.addAction(openAct)

    def openFile(self):
        fileName = QFileDialog.getOpenFileName(self.mainWindow, 'Open File', '/')
        if fileName != '' :
            if self.video_thread.isFinished() == False:
                self.video_thread.pause = False
                self.video_thread.__del__()
            self.isProcessing = False
            self.startSetAct.setIcon(QIcon('%s/gui/start.png' % self.current_dir))
            self.fileName = fileName
            self.video_thread.set_video_path(fileName)
            self.timeline.uncomfort_time_list = []

    def add_set_params_toolbar(self,MainWindow):
        self.startSetAct = QAction(QIcon('%s/gui/start.png'%self.current_dir), 'StartSet', MainWindow)
        self.startSetAct.triggered.connect(self.startProcess)
        self.toolbar = MainWindow.addToolBar('StartSet')
        self.toolbar.addAction(self.startSetAct)

    def startProcess(self):
        # isProcessing point out the state of startSecAct button
        if self.isProcessing == True:
            # pause video thread
            self.isProcessing = False
            self.video_thread.pause = True
            self.startSetAct.setIcon(QIcon('%s/gui/start.png' % self.current_dir))
        else:
            self.isProcessing = True
            self.startSetAct.setIcon(QIcon('%s/gui/pause.png' % self.current_dir))
            # check if just opened a new video
            # or just paused the video thread and want to continue
            if self.video_thread.pause == True:
                self.video_thread.pause = False
            else:
                if self.fileName == None:
                    QMessageBox.warning(self.mainWindow, "Message", "Please choose a video!")
                elif self.combobox_mode.currentIndex() == 0:
                    self.current_mode = 0
                    # 9 block mode
                    uncomfort_block_num = self.lineEdit_uncomfortBlockNum.text()
                    center_luma_thresh = self.lineEdit_centerThresh.text()
                    luma_diff_thresh = self.lineEdit_thresh.text()
                    color_uncomfort_block_num = self.lineEdit_colorUncomfortBlockNum.text()
                    color_center_luma_thresh = self.lineEdit_colorCenterThresh.text()
                    color_diff_thresh = self.lineEdit_colorThresh.text()
                    # if (len(uncomfort_block_num)*len(center_luma_thresh)*len(luma_diff_thresh) == 0):
                    #     QMessageBox.warning(self.mainWindow, "Message", "Please input parameters！")
                    # elif (len(color_uncomfort_block_num)*len(color_center_luma_thresh)*len(color_diff_thresh) == 0):
                    #     QMessageBox.warning(self.mainWindow, "Message", "Please input parameters！")
                    self.video_thread.set_luma_prarm(int(uncomfort_block_num), float(center_luma_thresh), float(luma_diff_thresh))
                    self.video_thread.set_color_prarm(int(color_uncomfort_block_num), float(color_center_luma_thresh), float(color_diff_thresh))
                    self.video_thread.set_mode(0)
                    self.video_thread.start()
                elif self.combobox_mode.currentIndex() == 1:
                    self.current_mode = 1
                    top_luma_thresh = self.lineEdit_uncomfortBlockNum.text()
                    center_luma_thresh = self.lineEdit_centerThresh.text()
                    bottom_luma_thresh = self.lineEdit_thresh.text()
                    top_color_thresh = self.lineEdit_colorUncomfortBlockNum.text()
                    center_color_thresh = self.lineEdit_colorCenterThresh.text()
                    bottom_color_thresh = self.lineEdit_colorThresh.text()
                    self.video_thread.set_3block_mode_luma_param(float(top_luma_thresh), float(center_luma_thresh), float(bottom_luma_thresh))
                    self.video_thread.set_3block_mode_color_param(float(top_color_thresh), float(center_color_thresh),
                                                                 float(bottom_color_thresh))
                    self.video_thread.set_mode(1)
                    self.video_thread.start()

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Uncomfortable Frame Detector")
        self.label_uncomfortBlockNum.setText( "luminance uncomfortable block number threshold")
        self.label_centerThresh.setText("center luminance difference threshold")
        self.label_thresh.setText("luminance difference threshold")
        self.label_colorUncomfortBlockNum.setText("color uncomfortable block number threshold    ")
        self.label_colorCenterThresh.setText("center color difference threshold    ")
        self.label_colorThresh.setText("color difference threshold    ")
        self.lineEdit_uncomfortBlockNum.setText('3')
        self.lineEdit_centerThresh.setText('10')
        self.lineEdit_thresh.setText('10')
        self.lineEdit_colorUncomfortBlockNum.setText('3')
        self.lineEdit_colorCenterThresh.setText('2.5')
        self.lineEdit_colorThresh.setText('2.5')


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = Window()
    MainWindow.show()
    sys.exit(app.exec_())

