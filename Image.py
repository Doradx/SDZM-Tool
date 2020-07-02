#!/usr/bin/python3
# -*-coding:utf-8 -*-

# Reference: **********************************************
# @Project   : code
# @File    : Image.py
# @Time    : 2020/6/15 21:25
# @License   : LGPL
# @Author   : Dorad
# @Email    : cug.xia@gmail.com
# @Blog      : https://blog.cuger.cn


import numpy as np
from PyQt5.QtGui import QImage, QPolygonF
from skimage import filters, measure, color, morphology, draw, segmentation


def narray2qimage(img):
    if img.shape[2] > 1:  # RGB image
        return QImage(img[:], img.shape[1], img.shape[0], img.shape[1] * 3, QImage.Format_RGB888)
    else:  # gray image
        return QImage(img[:], img.shape[1], img.shape[0], img.shape[1], QImage.Format_Grayscale8)


def qimage2narray(qimage):
    # TODO: Warn about other odd formats we don't currently handle properly,
    # such as the odd 16-bit packed formats QT supports
    arrayptr = qimage.bits()
    # QT may pad the image, so we need to use bytesPerLine, not width for
    # the conversion to a numpy array
    bytes_per_pixel = qimage.depth() // 8
    pixels_per_line = qimage.bytesPerLine() // bytes_per_pixel
    img_size = pixels_per_line * qimage.height() * bytes_per_pixel
    arrayptr.setsize(img_size)
    img = np.array(arrayptr)
    # Reshape and trim down to correct dimensions
    if bytes_per_pixel > 1:
        img = img.reshape((qimage.height(), pixels_per_line, bytes_per_pixel))
        img = img[:, :qimage.width(), :]
    else:
        img = img.reshape((qimage.height(), pixels_per_line))
        img = img[:, :qimage.width()]
    # Strip qt's false alpha channel if needed
    # and reorder color axes as required
    if bytes_per_pixel == 4 and not qimage.hasAlphaChannel():
        img = img[:, :, 2::-1]
    elif bytes_per_pixel == 4:
        img[:, :, 0:3] = img[:, :, 2::-1]
    return img


def imageWithPolygon2Label(img: QImage, polygon: QPolygonF, remove_small_objects=64, remove_small_holes=64):
    '''
    convert image with mask to label image.
    Args:
        img: QImage
        polygon:  QPolygonF
        label: np.array

    Returns:

    '''
    # convert QImage into numpy array
    imgArr = qimage2narray(img)
    # convert image into gray mode if it's rgb mode.
    gray = color.rgb2gray(imgArr)
    # polygon to binary mask
    mask = __QPolygon2Mask(gray.shape, polygon)
    # __otsuWithMask2bw
    bw = __otsuWithMask2bw(gray, mask)
    # remove small objects
    morphology.remove_small_objects(bw, min_size=remove_small_objects, connectivity=2, in_place=True)
    morphology.remove_small_holes(bw, area_threshold=remove_small_holes, connectivity=2, in_place=True)
    # binary image to label image
    label = morphology.label(bw, connectivity=2)
    return label


def imageLabelProperty(labelMask: np.array):
    return measure.regionprops(labelMask)


def imageLabelMerge(oldLabel, newLabel):
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

    newLabel, fw, inv = segmentation.relabel_sequential(newLabel, offset=oldLabel.max() + 1)
    indexClashedInNewLabel = np.logical_and(newLabel > 0, oldLabel > 0)
    newLabelClashed, indexN = np.unique(newLabel[indexClashedInNewLabel], return_index=True)
    newLabelClashed = newLabelClashed[np.argsort(indexN)]
    oldLabelClashed, indexO = np.unique(oldLabel[indexClashedInNewLabel], return_index=True)
    oldLabelClashed = oldLabelClashed[np.argsort(indexO)]

    for i in range(len(newLabelClashed)):
        newLabel[newLabel == newLabelClashed[i]] = oldLabelClashed[i]

    newLabel[indexClashedInNewLabel] = 0
    returnLabel, fw, inv = segmentation.relabel_sequential(oldLabel + newLabel)
    return returnLabel


def labelMask2Image(labelMask, labelProperty):
    pass


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
    otsu = filters.threshold_otsu(masked.compressed())
    print('OTSU: %s' % otsu)
    # convert gray image under mask into binary image
    # maskedImage = np.reshape(masked, img.shape)
    maskedImage = masked.filled(fill_value=0)
    bw = maskedImage >= otsu
    return bw


def __QPolygon2Mask(imageShape: np.array, polygon: QPolygonF):
    poa = np.empty([len(polygon), 2])
    for i, p in enumerate(polygon):
        poa[i, :] = [p.x(), p.y()]
        # poa = np.append(poa, [p.x(), p.y()])
    return draw.polygon2mask(imageShape, poa)


def __label2polygon(labelImage):
    '''
    convert label image into QPolygon list
    Args:
        labelImage:

    Returns:

    '''
    pass


if __name__ == '__main__':
    print('开始处理')
    # img_path = './res/SY3.JPG'
    # # # load image with QImage
    # img = QImage(img_path)
    # # QImage to narray
    # # arr = qimage2narray(img)
    # # a = io.imread('./res/SY1.JPG')
    # # io.imshow(arr)
    # # # imageWithMask2Label
    # polygon = QPolygonF()
    # polygon.append(QPointF(1500, 1100))
    # polygon.append(QPointF(1500, 2500))
    # polygon.append(QPointF(2300, 2500))
    # polygon.append(QPointF(2300, 1100))
    # # label = imageWithPolygon2Label(img, polygon)
    # # pass
    # a = io.imread(img_path)
    # label = imageWithPolygon2Label(img, polygon, remove_small_objects=512)
    # print('Label Count: %s' % np.max(label))
    # io.imshow(color.label2rgb(label, bg_label=0, image=a, alpha=0.25))
    # io.show()

    # test imageLabelMerge
    # a = np.array([
    #     [1, 1],
    #     [2, 2],
    #     [0, 0]
    # ])
    # b = np.array([
    #     [0, 4],
    #     [2, 2],
    #     [2, 3]
    # ])
    # c = imageLabelMerge(a, b)
    # print(c)
    pass
