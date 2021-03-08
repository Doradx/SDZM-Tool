# -*- coding: utf-8 -*-

# @FileName: ColorCircle.py
# @Time    : 2021-03-03 10:25
# @Author  : Dorad, cug.xia@gmail.com
# @Blog    ：https://blog.cuger.cn

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import numpy as np


class ColorCircle(QWidget):
    def __init__(self, radius=100.0):
        QWidget.__init__(self)
        self.radius = radius
        self.setFixedSize(radius * 2, radius * 2)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, ev):
        QWidget.paintEvent(self, ev)
        p = QPainter(self)
        for i in range(self.width()):
            for j in range(self.height()):
                angle = np.arctan2(i - self.radius, j - self.radius) + np.pi
                r = np.sqrt(np.power(i - self.radius, 2) + np.power(j - self.radius, 2))
                color = self.getColorByAngleAndRP(angle, r / self.radius)
                p.setPen(color)
                p.drawPoint(i, j)

    def getColorByAngleAndRP(self, angle, radiusPercentage):
        color = QColor(255, 255, 255, 0)
        h = angle / (2. * np.pi)
        v = radiusPercentage
        s = 1.0
        if v <= 1.0:
            color.setHsvF(h, s, v, 1.0)
        return color

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = ColorCircle()
    w.show()
    app.exec()
