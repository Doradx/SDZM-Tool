#!/usr/bin/python3
# -*-coding:utf-8 -*-

# Reference: **********************************************
# @Project   : code
# @File    : ImageViewerWithPolygon.py
# @Time    : 2020/6/22 9:08
# @License   : LGPL
# @Author   : Dorad
# @Email    : cug.xia@gmail.com
# @Blog      : https://blog.cuger.cn

from uuid import uuid4

from PyQt5.QtCore import QPointF, pyqtSignal, QLineF, Qt, QPoint
from PyQt5.QtGui import QIcon, QPolygonF, QColor, QMouseEvent, QKeyEvent, QImage, QPainter, QPainterPath
from PyQt5.QtWidgets import QWidget, QPushButton

from ImageViewer import ImageViewer


class ImageViewerWithPolygon(ImageViewer):
    PolygonListUpdatedSignal = pyqtSignal([str, object], name='Polygon List Updated')
    PolygonDrawFinishedSignal = pyqtSignal([str, QPolygonF], name='Real Time Polygon Draw Finished')
    LineDrawFinishedSIgnal = pyqtSignal([str, QLineF], name='Real Time Line Draw Finished')

    def __init__(self, allowAddPolygonManually=True, allowDelPolygonManually=True):
        super(ImageViewerWithPolygon, self).__init__()
        # additional property for polygon
        self.PolygonSelectedColor = QColor(0, 0, 255, 100)
        self.PolygonColor = QColor(0, 0, 255, 40)
        self.tmpPolygonColor = QColor(255, 0, 0, 20)
        self.allowAddPolygonManually = allowAddPolygonManually
        self.allowDelPolygonManually = allowDelPolygonManually

        self.setMouseTracking(True)

    '''
    over load methods
    '''

    def initUi(self):
        ImageViewer.initUi(self)
        # self.polygonDrawing = False
        self.polygonList = []  # {geo:'',results:'', type:'', selected:False}
        # self.tmpPolygon = QPolygonF()
        self.tmpDrawPoints = []
        self.drawModel = 'polygon'  # 0. scaleLine, 1. cropPolygon, 2. polygon
        self.drawing = False
        # add polygon button
        polygonBtn = QPushButton(QIcon('./images/icons/polygon.png'), '')
        polygonBtn.setToolTip('Add Polygon')
        polygonBtn.clicked.connect(lambda: self.startDraw(mode='polygon'))
        self.toolBox.addWidget(polygonBtn)
        self.update()

    def paintEvent(self, event):
        ImageViewer.paintEvent(self, event)

        if self.drawing:
            self.pt.begin(self)
            self.pt.setPen(QColor('red'))
            self.pt.setBrush(QColor(255, 0, 0, 10))
            pp = QPolygonF()
            for p in self.tmpDrawPoints:
                pp.append(self._pix2real(p))
            pp.append(self.mousePos)
            self.pt.drawPolygon(pp)
            self.pt.end()

        if self.drawing:
            self.setCursor(Qt.CrossCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        ImageViewer.mousePressEvent(self, event)
        if event.button() == Qt.LeftButton:
            if self.drawing:
                # check draw type and points length.
                self.__draw(event.pos())
            else:
                # check if something is selected
                for idx, polygon in enumerate(self.polygonList):
                    p = polygon['geo']
                    if p.containsPoint(self._real2pix(event.pos()), Qt.OddEvenFill):
                        self.polygonList[idx]['selected'] = ~self.polygonList[idx]['selected']
                        self.update()
        elif event.button() == Qt.RightButton and self.drawing:
            # check if it's confirm of cancel
            self.__drawExit()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if self.drawing:
            if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and len(self.tmpPolygon) > 2:
                self.__drawExit()
            elif event.key() == Qt.Key_Escape:
                self.__drawExit()
            elif event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete:
                self.__delLastPointInTmpPolygon()
        else:
            if event.key() == Qt.Key_Delete and self.allowDelPolygonManually:
                self.delPolygonSelected()

    '''
    private methods
    '''

    def __draw(self, pos):
        self.tmpDrawPoints.append(self._real2pix(pos))
        if self.drawModel in ['line', 'scaleLine'] and len(self.tmpDrawPoints) > 1:
            self.__drawExit()

    def __drawExit(self):
        # reset status
        self.mouseLeftButtonDown = False
        self.drawing = False
        if self.drawModel in ['line', 'scaleLine']:
            if len(self.tmpDrawPoints) < 2:
                self.tmpDrawPoints = []
                return
            self.LineDrawFinishedSIgnal.emit(self.drawModel, QLineF(self.tmpDrawPoints[0], self.tmpDrawPoints[1]))
        elif self.drawModel in ['polygon', 'cropPolygon']:
            if len(self.tmpDrawPoints) < 3:
                self.tmpDrawPoints = []
                return
            polygon = QPolygonF()
            for p in self.tmpDrawPoints:
                polygon.append(p)
            if self.drawModel == 'polygon':
                self.__addPolygon({
                    'geo': polygon,
                    'selected': False
                })
            self.PolygonDrawFinishedSignal.emit(self.drawModel, polygon)
        self.drawModel = None
        self.tmpDrawPoints = []

    def __addPolygon(self, polygon: dict):
        if 'geo' not in polygon.keys():
            raise Exception('逆序指定geo')
        if 'selected' not in polygon.keys():
            polygon['selected'] = False
        polygon['uid'] = str(uuid4())
        self.polygonList.append(polygon)
        self.PolygonListUpdatedSignal.emit('add', polygon)
        self.update()
        return True

    def __delLastPointInTmpPolygon(self):
        if len(self.tmpDrawPoints) > 0:
            del self.tmpDrawPoints[len(self.tmpDrawPoints) - 1]
            self.update()

    '''
    public methods
    '''

    def startDraw(self, mode='line'):
        if mode not in ['scaleLine', 'line', 'polygon', 'cropPolygon'] or not self.Image:
            return
        self.drawModel = mode
        self.drawing = True
        self.tmpDrawPoints = []

    def selectPolygon(self, uid):
        for idx, polygon in enumerate(self.polygonList):
            if polygon['uid'] == uid:
                self.polygonList[idx]['selected'] = True
                self.PolygonListUpdatedSignal.emit('selected', polygon)
                break
        self.update()

    def unselectPolygon(self, uid):
        for idx, polygon in enumerate(self.polygonList):
            if polygon['uid'] == uid:
                self.polygonList[idx]['selected'] = False
                self.PolygonListUpdatedSignal.emit('unselected', polygon)
                break
        self.update()

    def selectAllPolygon(self):
        for idx, polygon in enumerate(self.polygonList):
            self.polygonList[idx]['selected'] = True
            self.PolygonListUpdatedSignal.emit('selected', polygon)
        self.update()

    def unselectAllPolygon(self):
        for idx, polygon in enumerate(self.polygonList):
            self.polygonList[idx]['selected'] = False
            self.PolygonListUpdatedSignal.emit('unselected', polygon)
        self.update()

    def delPolygonSelected(self):
        unselectedPolygonList = []
        for idx, polygon in enumerate(self.polygonList):
            if not polygon['selected']:
                unselectedPolygonList.append(polygon)
            else:
                self.PolygonListUpdatedSignal.emit('delete', polygon)
        self.polygonList = unselectedPolygonList
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
        # draw polygon
        if len(self.polygonList):
            for polygon in self.polygonList:
                # pp = QPolygonF([QPointF(point[0], point[1]) for point in polygon['geo']])
                if polygon['selected']:
                    painter.setPen(self.PolygonSelectedColor)
                    painter.setBrush(self.PolygonSelectedColor)
                else:
                    painter.setPen(self.PolygonColor)
                    painter.setBrush(self.PolygonColor)
                painter.drawPolygon(polygon['geo'])
        painter.end()
        if remove_useless_background and self.cropPolygon:
            return paintedImage.copy(painterPath.boundingRect().toRect())
        else:
            return paintedImage
