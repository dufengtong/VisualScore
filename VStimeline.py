# -*- coding: utf-8 -*-

# coding by dft
# create a time line widget that can be scaled scrolled and clicked

import sys
from PyQt5 import QtCore, QtGui, QtWidgets




class VStimelineWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # time line is activated when user select a video
        self.isactivated = True
        # self.default_width = 1000
        # self.default_height = 200
        # # self.scene = QtWidgets.QGraphicsScene()
        # # self.view = QtWidgets.QGraphicsView(self.scene)
        # desktop = QtWidgets.QApplication.desktop()
        # screenW = desktop.screenGeometry().width()
        # screenH = desktop.screenGeometry().height()
        # self.setGeometry(screenW/2-self.default_width/2, screenH/2-self.default_height/2, self.default_width,self.default_height)

        # add scroll bar
        self.scrollArea = QtWidgets.QScrollArea(self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.scrollArea)


        # self.resize(1000,200)
        palette1 = QtGui.QPalette()
        palette1.setColor(self.backgroundRole(), QtGui.QColor(255, 255, 255))  # 设置背景颜色
        self.setPalette(palette1)
        self.maxtime = 1200.0 # second
        self.default_unit_num = 100 # divide time line in to 500 units by default
        # max time of time line without scale is 100 units 100*5s=500 second
        if self.maxtime <= 500:
            self.dt = self.maxtime / self.default_unit_num  # ceil, second per unit length
            print(self.dt)
            self.unit_number = int(self.default_unit_num)
        else:
            self.dt = 5  # 5 second per unit
            self.unit_number = int(-(- self.maxtime // 5))  # total number of units

    def paintEvent(self, event):
        print(self.size())

        if self.isactivated:
            # set up painter
            painter = QtGui.QPainter(self)
            painter.setPen(QtGui.QPen(QtCore.Qt.black))

            # draw base time line
            self.timeline = QtCore.QLine(0, self.height()/2, self.width(), self.height()/2)
            painter.drawLine(self.timeline)

            # draw scale on the time line
            length_per_unit = self.width() / self.default_unit_num
            # self.resize(self.unit_number * length_per_unit, 200)

            # self.scene.setSceneRect(0, 0, self.unit_number*length_per_unit, self.height()())

            # draw a long line every 10 dt
            for i in range(self.unit_number):
                if i%10 == 0:
                    painter.drawLine(length_per_unit * i, self.height() / 2, length_per_unit * i, self.height() / 2 - 10)
                    # painter.setPen(QtGui.QColor(168, 34, 3))
                    painter.setFont(QtGui.QFont('Decorative', 8))
                    m, s = divmod(self.dt*i, 60)
                    painter.drawText(QtCore.QRect(length_per_unit * i - 4.7*length_per_unit,self.height() / 2 - 30,10*length_per_unit,20),QtCore.Qt.AlignCenter, '%02d:%02d'%(m,s))
                else:
                    painter.drawLine(length_per_unit * i, self.height()/2 , length_per_unit*i, self.height()/2 - 5)


# class timelineView(QtWidgets.QGraphicsView):
#     def __init__(self):
#         super().__init__()
#         self.widget = VStimelineWidget()
#         self.scene = QtWidgets.QGraphicsScene()
#         self.scene.setSceneRect(0,0,1000,200)
#         self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
#
#     def paintEvent(self, QPaintEvent):
#         self.scene.addLine(0,0,1000,100)




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    timeline = VStimelineWidget()

    default_width = 1000
    default_height = 200
    desktop = QtWidgets.QApplication.desktop()
    screenW = desktop.screenGeometry().width()
    screenH = desktop.screenGeometry().height()
    timeline.setGeometry(screenW/2-default_width/2, screenH/2-default_height/2, default_width,default_height)
    timeline.show()

    sys.exit(app.exec_())