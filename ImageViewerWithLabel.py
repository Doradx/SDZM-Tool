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

    '''
    over load methods
    '''

    def initUi(self):
        '''
        label mask property
        '''
        ImageViewer.initUi(self)
        self.labelMask = np.array([])
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
        from skimage import color
        labelImg = color.label2rgb(self.labelMask, image=ImageViewerWithLabel.__qimage2narray(self.Image), bg_label=0,
                                   alpha=0.25)
        # labelImg=ImageViewerWithLabel.__qimage2narray(self.Image)
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
        # polygon to binary mask
        mask = ImageViewerWithLabel.__QPolygon2Mask(gray.shape, polygon)
        # __otsuWithMask2bw
        bw = ImageViewerWithLabel.__otsuWithMask2bw(gray, mask)
        # remove small objects
        morphology.remove_small_objects(bw, min_size=self.remove_small_objects, connectivity=2, in_place=True)
        morphology.remove_small_holes(bw, area_threshold=self.remove_small_holes, connectivity=2, in_place=True)
        # binary image to label image
        label = morphology.label(bw, connectivity=2)
        self.addLabelMask(label)

    def deletePolygonArea(self, polygon: QPolygonF):
        # polygon to binary mask
        mask = ImageViewerWithLabel.__QPolygon2Mask(self.labelMask.shape, polygon)
        # remove mask area
        self.labelMask[mask > 0] = 0
        self.updatePaintImage()


    def deleteLabels(self, labels):
        assert type(labels) == list
        for label in labels:
            # delete label
            self.labelMask[self.labelMask == label] = 0
            # update label property
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
    def __imageLabelMerge(oldLabel, newLabel):
        '''
        merge labels with no repeat label id.
        Args:
            oldLabel:
            newLabel:

        Returns: merged label without repeat label id
        '''
        assert type(oldLabel) == np.ndarray
        assert type(newLabel) == np.ndarray

        if oldLabel.shape != newLabel.shape:
            raise Exception('New label mask and old label mask must have the same size.')

        from skimage import segmentation
        newLabel, fw, inv = segmentation.relabel_sequential(newLabel, offset=oldLabel.max() + 1)
        indexClashedInNewLabel = np.logical_and(newLabel > 0, oldLabel > 0)
        newLabelClashed, indexN = np.unique(newLabel[indexClashedInNewLabel], return_index=True)
        newLabelClashed = newLabelClashed[np.argsort(indexN)]
        oldLabelClashed, indexO = np.unique(oldLabel[indexClashedInNewLabel], return_index=True)
        oldLabelClashed = oldLabelClashed[np.argsort(indexO)]

        for i in range(len(newLabelClashed)):
            newLabel[newLabel == newLabelClashed[i]] = oldLabelClashed[i]

        newLabel[indexClashedInNewLabel] = 0
        label = np.around(oldLabel + newLabel).astype(np.int)
        returnLabel, fw, inv = segmentation.relabel_sequential(label)
        return returnLabel


if __name__ == '__main__':
    print('Start')
    imagePath = './res/SY4.JPG'

    app = QApplication(sys.argv)
    demo = ImageViewerWithLabel()
    demo.setImage(imagePath=imagePath)


    def p(old, new):
        print('缩放: %s -> %s' % (old, new))


    demo.ScaleChangedSignal.connect(p)


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
