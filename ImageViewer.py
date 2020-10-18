#!/usr/bin/python3
# -*-coding:utf-8 -*-

# Reference: **********************************************
# @Project   : code
# @File    : ImageViewer.py
# @Time    : 2020/6/6 15:36
# @License   : LGPL
# @Author   : Dorad
# @Email    : cug.xia@gmail.com
# @Blog      : https://blog.cuger.cn

import os
import sys

import numpy as np
from PyQt5.QtCore import QPointF, pyqtSignal, Qt, QPoint, QRect, QLineF
from PyQt5.QtGui import QIcon, QColor, QPalette, QPainter, QResizeEvent, QWheelEvent, QMouseEvent, QKeyEvent, QImage, \
    QPolygonF, QPainterPath
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout, QHBoxLayout


class ImageViewer(QWidget):
    MousePosChangedSignal = pyqtSignal([QPointF], name='Mouse Pos Changed')
    ViewPointChangeSignal = pyqtSignal([QPointF, QPointF, float, float], name='View Point Changed')

    def __init__(self):
        super(ImageViewer, self).__init__()
        self.setMouseTracking(True)
        # moniter = QApplication.desktop().size()
        moniter = QApplication.primaryScreen().size()
        self.resize(int(moniter.width() / 1.5), int(moniter.height() / 1.5))
        self.initUi()

    def initUi(self):
        self.ImagePath = None  # 原始图片路径
        self.Image = None  # 图像

        self.cropPolygon = None  # 裁剪边框

        # private property
        self.mousePos = QPointF(0, 0)
        self.mouseLeftButtonDown = False

        self.scale = 1  # 比例
        self.offset = QPointF(0, 0)  # 初始坐标

        self.backgroundColor = QColor("#898989")
        # button
        self.zoomInBtn = QPushButton(QIcon('images/icons/zoom-in.png'), '')
        self.zoomInBtn.setToolTip('Zoom In')
        self.zoomInBtn.clicked.connect(self.zoomIn)
        self.zoomOutBtn = QPushButton(QIcon('images/icons/zoom-out.png'), '')
        self.zoomOutBtn.setToolTip('Zoom Out')
        self.zoomOutBtn.clicked.connect(self.zoomOut)
        self.reloadBtn = QPushButton(QIcon('./images/icons/expand.png'), '')
        self.reloadBtn.setToolTip('Center')
        self.reloadBtn.clicked.connect(self.setImageCenter)

        # layout
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addStretch(1)
        self.toolBox = QHBoxLayout()
        self.toolBox.addStretch(1)
        self.toolBox.addWidget(self.zoomInBtn)
        self.toolBox.addWidget(self.zoomOutBtn)
        self.toolBox.addWidget(self.reloadBtn)
        self.mainLayout.addLayout(self.toolBox)
        self.setLayout(self.mainLayout)

    def paintEvent(self, event):
        if self.mouseLeftButtonDown:
            self.setCursor(Qt.SizeAllCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        self.backgroundPalette = QPalette()
        self.backgroundPalette.setColor(self.backgroundRole(), self.backgroundColor)
        self.setPalette(self.backgroundPalette)
        self.setAutoFillBackground(True)
        self.pt = QPainter()
        if self.Image:
            renderImage = self.renderImage()
            scaledImage = renderImage.scaled(int(renderImage.size().width() * self.scale),
                                             int(renderImage.size().height() * self.scale))
            self.pt.begin(self)
            self.pt.drawImage(self.offset, scaledImage)
            self.pt.end()
        self.draw_axis()

    def draw_axis(self):
        # get size of widget
        width = self.size().width()
        height = self.size().height()
        axisLength = 100
        axisOriginPoint = QPoint(20, height - 20)
        PLU = QPoint(0, -10) + axisOriginPoint
        PL = QPoint(0, 0) + axisOriginPoint
        PR = QPoint(axisLength, 0) + axisOriginPoint
        PRU = QPoint(axisLength, -10) + axisOriginPoint
        textRect = QRect(PL - QPoint(0, 20), PR)
        self.pt.begin(self)
        lines = [
            QLineF(PLU, PL),
            QLineF(PL, PR),
            QLineF(PR, PRU)
        ]
        self.pt.drawLines(lines)
        self.pt.drawText(textRect, Qt.AlignCenter, str(np.around(axisLength / self.scale, 2)) + 'PX')
        self.pt.end()

    def resizeEvent(self, event: QResizeEvent) -> None:
        pass

    def wheelEvent(self, event: QWheelEvent) -> None:
        step = event.angleDelta().y() / 8 / 150  # one step, 0.1
        pos = event.position()
        print('鼠标滚轮滚动, X: %s, Y: %s, Step: %s' % (pos.x(), pos.y(), step))
        if step > 0:
            self.zoomIn(pos=pos, p=abs(step))
        else:
            self.zoomOut(pos=pos, p=abs(step))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            print('鼠标左键单击: %s, %s' % (event.x(), event.y()))
            self.mouseLeftButtonDown = True
            self.mousePos = event.pos()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            print('鼠标左键释放: %s, %s' % (event.x(), event.y()))
            self.mouseLeftButtonDown = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.mouseLeftButtonDown:
            print('鼠标左键拖移: %s, %s' % (event.x(), event.y()))
            posDiff = event.pos() - self.mousePos
            print('移动量: %s, %s' % (posDiff.x(), posDiff.y()))
            # self.offset = self.offset + posDiff
            self.setViewPoint(offset=self.offset + posDiff)

        self.mousePos = event.pos()
        self.MousePosChangedSignal.emit(self._real2pix(event.pos()))
        self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        pass

    def _pix2real(self, pos: QPointF):
        return pos * self.scale + self.offset

    def _real2pix(self, pos: QPointF):
        return (pos - self.offset) / self.scale

    def setImage(self, imagePath=None, image=None):

        if not os.path.exists(imagePath) and image == None:
            raise Exception('Error image path.')
        self.initUi()
        try:
            if image and type(image) == QImage:
                self.Image = image
            else:
                self.ImagePath = imagePath
                self.Image = QImage(self.ImagePath)
            self.update()

        except Exception as e:
            raise e
        self.setImageCenter()

    def setImageCenter(self):
        if not self.Image:
            return None
        self.setViewPoint(scale=min(self.size().width() / self.Image.size().width(),
                                    self.size().height() / self.Image.size().height()))
        # self.setScale(min(self.size().width() / self.Image.size().width(),
        #                   self.size().height() / self.Image.size().height()))
        offsetX = (self.size().width() - self.Image.width() * self.scale) / 2
        offsetY = (self.size().height() - self.Image.height() * self.scale) / 2
        self.setViewPoint(offset=QPointF(offsetX, offsetY))
        self.update()

    def setViewPoint(self, offset=None, scale=None):
        if not self.Image:
            return None
        oldOffset = False
        oldScale = False
        if offset and not offset == self.offset:
            oldOffset = self.offset
            self.offset = offset
        if scale and not scale == self.scale:
            oldScale = self.scale
            self.scale = scale
        if oldOffset or oldScale:
            self.ViewPointChangeSignal.emit(oldOffset if oldOffset else self.offset, self.offset,
                                            oldScale if oldScale else self.scale, self.scale)
            self.update()

    def zoomIn(self, pos=None, p=0.1):
        if not self.Image:
            return None
        if not pos:
            pos = QPointF(self.size().width() / 2, self.size().height() / 2)
        self.setViewPoint(scale=self.scale * (1 + p), offset=self.offset - (pos - self.offset) * p)
        self.update()

    def zoomOut(self, pos=None, p=0.1):
        if not self.Image:
            return None
        if not pos:
            pos = QPointF(self.size().width() / 2, self.size().height() / 2)
        self.setViewPoint(scale=self.scale * (1 - p), offset=self.offset + (pos - self.offset) * p)
        self.update()

    def setCropPolygon(self, polygon: QPolygonF):
        self.cropPolygon = polygon
        self.update()

    def renderImage(self, remove_useless_background=False):
        if not self.Image:
            return
        paintedImage = QImage(self.Image.size(), QImage.Format_ARGB32)
        paintedImage.fill(Qt.transparent)
        painter = QPainter(paintedImage)
        if self.cropPolygon:
            painterPath = QPainterPath()
            painterPath.addPolygon(self.cropPolygon)
            painter.setClipPath(painterPath)
        painter.drawImage(QPoint(), self.Image)
        painter.end()
        if remove_useless_background:
            return paintedImage.copy(painterPath.boundingRect().toRect())
        else:
            return paintedImage


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = ImageViewer()
    demo.setImage(imagePath='./res/SY1.JPG')


    def p(old, new):
        print('缩放: %s -> %s' % (old, new))


    # demo.ScaleChangedSignal.connect(p)

    def mouseUpdate(pos):
        print('鼠标移动监听: %s, %s' % (pos.x(), pos.y()))


    demo.MousePosChangedSignal.connect(mouseUpdate)
    demo.zoomOutBtn.setEnabled(True)
    demo.show()
    sys.exit(app.exec_())
