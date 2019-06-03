###########################################################################
# Covert .ui file to .py
#    pyside2-uic "C:\Users\LR Admin\QtProjects\ui_rot2d\mainwindow.ui" -o "C:\Users\LR Admin\PycharmProjects\qt_stuff\gui_2d_kinematics.py"
###########################################################################

import numpy as np
import math
import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsLineItem, QGraphicsScene, QGraphicsPixmapItem
from PySide2.QtCore import QLineF, Qt, QPoint, Slot
from PySide2.QtGui import QBrush, QPixmap, QPen, QPainter, QPaintDevice, QColor
from gui_2d_kinematics import Ui_MainWindow

'''
'points' uses angles[1:] and defines points in each coordinate frame
'lengths' uses angles[] and each each coordinate frame will have point (lengths[i], 0)
'equation' uses: Xo = R(a0)[L1;0] + R(a0)R(a1)[L2;0] + R(a0)R(a1)R(a2)[L3;0] + ...
'''
lengths = [140, 100, 70]; angles = [60, 45, -80]
points = [(1,3), (1,3), (1,3)]
PRECISION = 4
THRESH = 1e-3

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        #      Kinematics Graphics Setup
        self.pen = QPen(Qt.black, 3, Qt.DashDotLine, Qt.RoundCap, Qt.RoundJoin)
        self.graphicsScene = QGraphicsScene()
        self.graphicsView.setScene(self.graphicsScene)
        self.graphicsView.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        self.graphicsView.show()
        #      Other Widget Initializations
        self.verticalSlider.setSliderPosition(angles[0])
        self.verticalSlider_2.setSliderPosition(angles[1])
        self.verticalSlider_3.setSliderPosition(angles[2])
        self.textEdit.setPlainText(str(round(lengths[0], PRECISION)))
        self.textEdit_2.setPlainText(str(round(lengths[1], PRECISION)))
        self.textEdit_3.setPlainText(str(round(lengths[2], PRECISION)))
        self.label.setText(str(angles[0]))
        self.label_2.setText(str(angles[1]))
        self.label_3.setText(str(angles[2]))
        self.connect()
        self.draw_2d()

    def connect(self):
        self.verticalSlider.valueChanged[int].connect(self.angle1)
        self.verticalSlider_2.valueChanged[int].connect(self.angle2)
        self.verticalSlider_3.valueChanged[int].connect(self.angle3)
        self.textEdit.textChanged.connect(self.length1)
        self.textEdit_2.textChanged.connect(self.length2)
        self.textEdit_3.textChanged.connect(self.length3)
    '''
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setPen(QPen(Qt.green, 3))
        painter.setPen(QColor(0, 0, 255))
        painter.drawEllipse(QPoint(100, 100), 60, 60)
        painter.end()
    '''
    def draw_2d(self):
        self.graphicsScene.clear()
        point, line = [], []
        point.append((0, 0))
        for i in range(1,4):
            point.append((point[i-1][0] + (lengths[i-1] * math.cos(np.deg2rad(-sum(angles[:i])))),
                          point[i-1][1] + (lengths[i-1] * math.sin(np.deg2rad(-sum(angles[:i]))))))
            line.append(QGraphicsLineItem(point[i-1][0], point[i-1][1], point[i][0], point[i][1]))
            self.graphicsScene.addItem(line[i-1])
        self.label_5.setText("[" + str(round(point[3][0], PRECISION)) + ", " + str(round(-point[3][1], PRECISION)) + "]")

    @Slot()
    def angle1(self, value):
        angles[0] = value
        self.label.setText(str(value))
        self.draw_2d()

    @Slot()
    def angle2(self, value):
        angles[1] = value
        self.label_2.setText(str(value))
        self.draw_2d()

    @Slot()
    def angle3(self, value):
        angles[2] = value
        self.label_3.setText(str(value))
        self.draw_2d()

    @Slot()
    def length1(self):
        lengths[0] = float(self.textEdit.toPlainText())
        self.draw_2d()

    @Slot()
    def length2(self):
        lengths[1] = float(self.textEdit_2.toPlainText())
        self.draw_2d()

    @Slot()
    def length3(self):
        lengths[2] = float(self.textEdit_3.toPlainText())
        self.draw_2d()

def by_points():
    result = np.eye(3)
    for point, angle in zip(points[:-1], angles[1:]):
        tmp = np.array([
            [math.cos(np.deg2rad(angle)), -math.sin(np.deg2rad(angle)), point[0]],
            [math.sin(np.deg2rad(angle)), math.cos(np.deg2rad(angle)), point[1]],
            [0, 0, 1]
        ])
        result = result @ tmp
        result[np.abs(result) < THRESH] = 0

    tmp = np.array([[1, 0, points[-1][0]], [0, 1, points[-1][1]], [0, 0, 1]])
    return result @ tmp

def by_lengths():
    result = np.array([
        [math.cos(np.deg2rad(angles[0])), -math.sin(np.deg2rad(angles[0])), 0],
        [math.sin(np.deg2rad(angles[0])), math.cos(np.deg2rad(angles[0])), 0],
        [0, 0, 1]
    ])
    idx = 0
    for length, angle in zip(lengths[:-1], angles[1:]):
        idx += 1
        tmp = np.array([
            [math.cos(np.deg2rad(angle)), -math.sin(np.deg2rad(angle)), length],
            [math.sin(np.deg2rad(angle)), math.cos(np.deg2rad(angle)), 0],
            [0, 0, 1]
        ])
        result = result @ tmp
        result[np.abs(result) < THRESH] = 0
        #print("Point", idx, ": [", result[0][2], ",", result[1][2], "]")

    tmp = np.array([[1, 0, length], [0, 1, 0], [0, 0, 1]])
    return result @ tmp

def by_equation():
    end_effector = np.zeros((2, len(lengths)))
    for i in range(len(lengths), 0, -1):
        rotation = np.eye(2)
        for j in range(0, i):
            rotation = rotation @ rot(angles[j])
        end_effector[:,i-1] = (rotation @ np.array([[lengths[i-1]], [0]])).ravel()
    return end_effector

def rot(angle):
    return np.array([
        [math.cos(np.deg2rad(angle)), -math.sin(np.deg2rad(angle))],
        [math.sin(np.deg2rad(angle)), math.cos(np.deg2rad(angle))]
    ])

def print_points():
    po = by_points()
    le = by_lengths()
    eq = by_equation()
    print("End effector by_points is:   [", po[0][2], ",", po[1][2], "]")
    print("End effector by_lengths is:  [", le[0][2], ",", le[1][2], "]")
    print("End effector by_equation is: [", np.sum(eq[0]), ",", np.sum(eq[1]), "]")
    print("-----------------------------------------------------------------------")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())