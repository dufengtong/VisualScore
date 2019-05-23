import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse


class uncomfortPoint():
    def __init__(self, id, frame_idx, time):
        self.id = id
        self.frame_idx = frame_idx
        self.time = time

class timelineW(FigureCanvas):
    setUncomfortFrames = pyqtSignal(int)
    def __init__(self):
        self.figure = Figure()
        super(timelineW, self).__init__(self.figure)
        self.default_width = 1300
        self.resize(self.default_width, 150)
        self.scale = 1.0
        self.mouse_click_position = None

        self.isactivated = True
        self.video_length = 200.0  # second
        self.uncomfort_time_list = []
        # one second for one pixel

        self.default_unit_length = 5  # 5 pixel length per unit by default
        self.default_dt = 5  # 5 second per unit by default
        self.resetVideoLength(self.video_length)
        self.changeXYRatio()
        self.wheelEventBaseWidth = self.width()

    def mousePressEvent(self, eventQMouseEvent):
        self.mouse_click_position = eventQMouseEvent.pos()
        x = self.mouse_click_position.x()
        y = self.mouse_click_position.y()
        min_distance = 100
        selected_uncomfort_point = None
        # check if click near the timeline
        if abs(y-self.height()/2) < 15:
            # find the uncomfort time which is nearest to the click position
            for uncomfort_point in self.uncomfort_time_list:
                uncomfort_x = self.unit_length *uncomfort_point.time / self.dt
                distance = abs(x - uncomfort_x)
                if uncomfort_point.id == 0:
                    min_distance = distance
                    selected_uncomfort_point = uncomfort_point
                elif distance < min_distance:
                    min_distance = distance
                    selected_uncomfort_point = uncomfort_point

        if min_distance < 15:
            self.setUncomfortFrames.emit(selected_uncomfort_point.frame_idx)

    def wheelEvent(self, eventQWheelEvent):
        oldscale = self.scale
        self.scale += eventQWheelEvent.delta() / 1200.0
        if (self.scale < 1):
            self.scale = 1
        if self.scale >= 1:
            self.resize(self.wheelEventBaseWidth*self.scale, self.height())
            self.unit_length = self.width() * self.default_unit_length / self.video_length
            self.plot_timeline()

    def resetVideoLength(self, video_length):
        self.video_length = video_length
        self.default_unit_num = -int(
            -self.video_length / self.default_unit_length)  # divide time line in to 500 units by default
        if (self.default_unit_length * self.default_unit_num) > self.width():
            self.resize(self.default_unit_length * self.default_unit_num, self.height())
            self.unit_number = self.default_unit_num
            self.dt = self.default_dt
            self.unit_length = self.default_unit_length
        else:
            self.unit_length = self.width() * self.default_unit_length / self.video_length
            self.unit_number = self.default_unit_num
            self.dt = self.default_dt

        self.plot_timeline()

    def changeXYRatio(self):
        x0, y0 = self.ax.transAxes.transform((0, 0))  # lower left in pixels
        x1, y1 = self.ax.transAxes.transform((1, 1))  # upper right in pixes
        dx = x1 - x0
        dy = y1 - y0
        maxd = max(dx, dy)
        self.width_coefficient = maxd / dx
        self.height_coefficient = maxd / dy

    # only called when window is resized
    def plot_timeline(self, areaSize=None):
        if areaSize and (areaSize.width() > (self.unit_number*self.unit_length)):
            self.unit_length = self.width() * self.default_unit_length / self.video_length
            self.resize(areaSize.width(), self.height())
            self.wheelEventBaseWidth = self.width()
        self.ax = self.figure.add_subplot(111)
        self.ax.clear()
        self.ax.set_xlim(0, self.unit_number*self.unit_length)
        self.ax.set_ylim(0, self.height())
        if self.scale == 1:
            self.changeXYRatio()
        self.ax.axhline(self.height() / 2, color='k')
        for i in range(self.unit_number):
            if i % 10 == 0:
                self.ax.plot([self.unit_length * i, self.unit_length * i], [self.height() / 2, self.height() / 2 + 10], 'k')
                m, s = divmod(self.dt * i, 60)
                self.ax.text(self.unit_length * i,(self.height() / 2 + 30),'%02d:%02d'%(m,s),fontsize=10,ha='center')
            else:
                self.ax.plot([self.unit_length * i, self.unit_length * i], [self.height() / 2, self.height() / 2 + 5], 'k')
        self.ax.get_xaxis().set_ticks([])
        self.ax.get_yaxis().set_ticks([])
        self.figure.tight_layout(pad=0, h_pad=0, w_pad=0)

        if len(self.uncomfort_time_list) != 0:
            for uncomfort_point in self.uncomfort_time_list:
                circle = Ellipse((self.unit_length * uncomfort_point.time / self.dt, self.height() / 2),
                                 8 * self.width_coefficient, 1 * self.height_coefficient, color='r')
                self.ax.add_artist(circle)
        self.draw()

    def addUncomfortPoint(self, uncomfort_frame_idx, fps):
        print uncomfort_frame_idx
        uncomfort_frame_time = uncomfort_frame_idx/float(fps)
        uncomfort_point = uncomfortPoint(len(self.uncomfort_time_list), uncomfort_frame_idx, uncomfort_frame_time)
        self.uncomfort_time_list.append(uncomfort_point)
        circle = Ellipse((self.unit_length*uncomfort_frame_time/self.dt, self.height()/2), 8*self.width_coefficient,1*self.height_coefficient, color='r')
        self.ax.add_artist(circle)
        self.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = timelineW()
    main.show()

    sys.exit(app.exec_())