#!/usr/bin/python3
# -*-coding:utf-8 -*-

# Reference: **********************************************
# @Project   : code
# @File    : ImageViewerWithLabel.py
# @Time    : 2020/6/20 19:23
# @License   : LGPL
# @Author   : Dorad
# @Email    : cug.xia@gmail.com
# @Blog      : https://blog.cuger.cn

import sys

import numpy as np
from PyQt5.QtCore import QPointF, Qt, QPoint
from PyQt5.QtGui import QImage, QPolygonF, QPainter, QPainterPath
from PyQt5.QtWidgets import QWidget, QApplication
from skimage import color, morphology

from ImageViewer import ImageViewer


class ImageViewerWithLabel(ImageViewer):
    def __init__(self, remove_small_objects=64, remove_small_holes=64):
        super(ImageViewerWithLabel, self).__init__()

        self.remove_small_objects = remove_small_objects
        self.remove_small_holes = remove_small_holes

        self.showLabelList = np.array([], dtype=int)

    '''
    over load methods
    '''

    def initUi(self):
        '''
        label mask property
        '''
        ImageViewer.initUi(self)
        self.labelMask = np.array([], dtype=int)
        self.labelColors = []
        self.remove_small_objects = 64
        self.remove_small_holes = 64
        self.paintImage = None
        self.update()

    def setImage(self, imagePath=None, image=None):
        # set image
        ImageViewer.setImage(self, imagePath, image)
        self.paintImage = self.Image
        # init mask property
        self.labelMask = np.zeros([self.Image.height(), self.Image.width()])
        self.labelColors = []
        # update update widget
        self.update()

    def updatePaintImage(self):
        self.paintImage = self.imageWithLabel2Mask()
        self.update()

    # def paintEvent(self, event):
    #     if self.mouseLeftButtonDown:
    #         self.setCursor(Qt.SizeAllCursor)
    #     else:
    #         self.setCursor(Qt.ArrowCursor)
    #     self.backgroundPalette = QPalette()
    #     self.backgroundPalette.setColor(self.backgroundRole(), self.backgroundColor)
    #     self.setPalette(self.backgroundPalette)
    #     self.setAutoFillBackground(True)
    #     self.pt = QPainter()
    #     if self.paintImage:
    #         scaledImage = self.paintImage.scaled(int(self.paintImage.size().width() * self.Scale),
    #                                              int(self.paintImage.size().height() * self.Scale))
    #         self.pt.begin(self)
    #         self.pt.drawImage(self.Offset, scaledImage)
    #         self.pt.end()
    #
    #     self.draw_axis()

    '''
    label mask operation methods
    '''

    def addLabelMask(self, labelMask):
        '''
        append label mask to exist mask.
        Args:
            labelMask: new label mask

        Returns:

        '''
        assert type(labelMask) == np.ndarray
        self.labelMask = ImageViewerWithLabel.__imageLabelMerge(self.labelMask, labelMask)
        # update view
        self.updatePaintImage()

    def imageWithLabel2Mask(self):
        labelMaskShown = np.zeros(self.labelMask.shape, dtype=int)
        if len(self.showLabelList) > 0:
            for label in self.showLabelList:
                labelMaskShown[self.labelMask == label] = label
        else:
            labelMaskShown = self.labelMask
        from skimage import color
        labelImg = color.label2rgb(labelMaskShown, image=ImageViewerWithLabel.__qimage2narray(self.Image), bg_label=0,
                                   alpha=0.25)
        return ImageViewerWithLabel.__narray2qimage(labelImg)

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
        painter.drawImage(QPoint(), self.paintImage)
        painter.end()
        if remove_useless_background and self.cropPolygon:
            return paintedImage.copy(painterPath.boundingRect().toRect())
        else:
            return paintedImage

    '''
    user operation
    '''

    def addPolygonArea(self, polygon: QPolygonF):
        # convert QImage into numpy array
        imgArr = ImageViewerWithLabel.__qimage2narray(self.Image)
        # convert image into gray mode if it's rgb mode.
        gray = color.rgb2gray(imgArr)
        # check if the polygon is inside the cropPolygon
        polygon = polygon.intersected(self.cropPolygon)
        # polygon to binary mask
        mask = ImageViewerWithLabel.__QPolygon2Mask(gray.shape, polygon)
        # __otsuWithMask2bw
        bw = ImageViewerWithLabel.__otsuWithMask2bw(gray, mask)
        # remove small objects
        # morphology.remove_small_objects(bw, min_size=self.remove_small_objects, connectivity=2, in_place=True)
        # morphology.remove_small_holes(bw, area_threshold=self.remove_small_holes, connectivity=2, in_place=True)
        # binary image to label image
        label = morphology.label(bw, connectivity=2)
        self.addLabelMask(label)

    def deletePolygonArea(self, polygon: QPolygonF):
        # polygon to binary mask
        mask = ImageViewerWithLabel.__QPolygon2Mask(self.labelMask.shape, polygon)
        # remove mask area
        self.labelMask[mask > 0] = 0
        self.updatePaintImage()

    # add Riss Polygons
    def addRissPolygons(self, polygons):
        # convert QImage into numpy array
        imgArr = ImageViewerWithLabel.__qimage2narray(self.Image)
        # convert image into gray mode if it's rgb mode.
        gray = color.rgb2gray(imgArr)
        maskedGrayImage = np.ma.masked_array(gray, ImageViewerWithLabel.__QPolygon2Mask(gray.shape, self.cropPolygon))
        # polygon to binary mask
        mask = np.empty(gray.shape)
        for polygon in polygons:
            mask += ImageViewerWithLabel.__QPolygon2Mask(gray.shape, polygon)
        mask = mask > 0
        # 获得像素值
        pixels = gray[mask > 0]
        # 计算 ROIs 中的灰度直方图
        # hist, bin_edges = np.histogram(pixels.flatten(), bins=255, range=(-0.5, 255.5))
        # 估算正态分布
        mu = np.mean(pixels)  # 计算均值
        sigma = np.std(pixels)
        # 计算 m+1.95o, 得到阈值
        threshold = mu + 1.96 * sigma
        # 二值化
        binary = maskedGrayImage > threshold
        label = morphology.label(binary, connectivity=2)
        print("RISS阈值: %f, 破坏像素数量： %d" % (threshold*255, np.sum(binary > 0)))
        self.addLabelMask(label)

    def setShowLabelList(self, showLabelList):
        self.showLabelList = showLabelList
        self.updatePaintImage()

    def deleteLabels(self, labels):
        assert type(labels) == list
        for label in labels:
            # delete label
            self.labelMask[self.labelMask == label] = 0
            # update label property
        self.updatePaintImage()

    def deleteAllLabels(self):
        self.labelMask[self.labelMask > 0] = 0
        self.updatePaintImage()

    def removeSmallBlocks(self, remove_small_blocks=64):
        bw = morphology.remove_small_objects(self.labelMask > 0, min_size=remove_small_blocks, connectivity=2)
        self.labelMask = morphology.label(bw, connectivity=2)
        self.updatePaintImage()

    def removeSmallHoles(self, remove_small_holes=64):
        bw = morphology.remove_small_holes(self.labelMask > 0, area_threshold=remove_small_holes, connectivity=2)
        self.labelMask = morphology.label(bw, connectivity=2)
        self.updatePaintImage()

    '''
    image operation
    '''

    @staticmethod
    def __narray2qimage(img):
        if img.dtype == 'float64':
            img = np.array(img * 255).astype(np.int)
        from qimage2ndarray import array2qimage
        return array2qimage(img)
        # if img.shape[2] > 1:  # RGB image
        #     return QImage(np.require(img, np.uint8, 'C'), img.shape[1], img.shape[0], img.shape[1] * 3,
        #                   QImage.Format_RGB888)
        # else:  # gray image
        #     return QImage(np.require(img, np.uint8, 'C'), img.shape[1], img.shape[0], img.shape[1],
        #                   QImage.Format_Grayscale8)

    @staticmethod
    def __qimage2narray(qimage):
        from qimage2ndarray import rgb_view
        return rgb_view(qimage=qimage)

    @staticmethod
    def __otsuWithMask2bw(img: np.array, mask: np.array):
        '''
        convert image with mask to binary image using otsu method.
        Args:
            img: np.array, two dimensions, gray image
            mask: np.array, two dimensions, binary image

        Returns:

        '''
        # calculate the threshold for the image under mask
        masked = np.ma.masked_array(img, mask == 0)
        from skimage import filters
        otsu = filters.threshold_otsu(masked.compressed())
        print('OTSU: %s' % otsu)
        # convert gray image under mask into binary image
        # maskedImage = np.reshape(masked, img.shape)
        maskedImage = masked.filled(fill_value=0)
        bw = maskedImage >= otsu
        return bw

    @staticmethod
    def __QPolygon2Mask(imageShape: np.array, polygon: QPolygonF):
        poa = np.empty([len(polygon), 2])
        for i, p in enumerate(polygon):
            poa[i, :] = [p.x(), p.y()]
            # poa = np.append(poa, [p.x(), p.y()])
        from skimage import draw
        mask = draw.polygon2mask([imageShape[1], imageShape[0]], poa)
        return mask.transpose()

    @staticmethod
    def __imageLabelMerge(oldLabel, newLabel=None):
        '''
        merge labels with no repeat label id.
        Args:
            oldLabel:
            newLabel:

        Returns: merged label without repeat label id
        '''

        if not newLabel.any():
            return oldLabel

        assert type(oldLabel) == np.ndarray
        assert type(newLabel) == np.ndarray

        if oldLabel.shape != newLabel.shape:
            newLabel = np.pad(newLabel,
                              ((0, oldLabel.shape[0] - newLabel.shape[0]), (0, oldLabel.shape[1] - newLabel.shape[1])),
                              'constant', constant_values=0)

        from skimage import measure
        relabeled = measure.label(oldLabel + newLabel > 0, connectivity=2, background=0)
        return relabeled


if __name__ == '__main__':
    print('Start')
    imagePath = './res/SY4.JPG'

    app = QApplication(sys.argv)
    demo = ImageViewerWithLabel()
    demo.setImage(imagePath=imagePath)


    def p(old, new):
        print('缩放: %s -> %s' % (old, new))


    # demo.ScaleChangedSignal.connect(p)

    def mouseUpdate(pos):
        print('鼠标移动监听: %s, %s' % (pos.x(), pos.y()))


    demo.MousePosChangedSignal.connect(mouseUpdate)
    demo.show()

    polygon = QPolygonF()

    polygon.append(QPointF(1000, 1000))

    polygon.append(QPointF(2500, 1000))

    polygon.append(QPointF(1000, 2500))

    demo.addPolygon(polygon)

    sys.exit(app.exec_())
