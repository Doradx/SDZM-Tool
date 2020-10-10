#!/usr/bin/python3
# -*-coding:utf-8 -*-

# Reference: **********************************************
# @Project   : code
# @File    : MainWindow.py
# @Time    : 2020/6/7 21:54
# @License   : LGPL
# @Author   : Dorad
# @Email    : cug.xia@gmail.com
# @Blog      : https://blog.cuger.cn


import datetime

import numpy as np
from PyQt5.QtCore import QPointF, QLineF, Qt, QUrl
from PyQt5.QtGui import QIcon, QPolygonF, QDesktopServices, QPixmap, QCloseEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication, QAction, QLabel, QProgressBar, QFileDialog, \
    QMessageBox, QInputDialog, QMainWindow, QProgressDialog

from ImageViewerWithLabel import ImageViewerWithLabel
from ImageViewerWithPolygon import ImageViewerWithPolygon


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUi()

    def initUi(self):

        '''
        ui
        Returns:

        '''

        # center widget
        self.setWindowTitle(
            'Shear Failure Regions of Rock Joints Measurement Tool v1.0.0 (By Dorad, cug_xia@cug.edu.cn)')
        self.setWindowIcon(QIcon('./images/icons/logo.png'))
        self.originView = ImageViewerWithPolygon(allowAddPolygonManually=True, allowDelPolygonManually=True)
        self.resultView = ImageViewerWithLabel()

        operationVBox = QVBoxLayout()
        # layout
        topHBox = QHBoxLayout()
        viewHBox = QHBoxLayout()
        viewHBox.addWidget(self.originView)
        viewHBox.addWidget(self.resultView)
        topHBox.addLayout(viewHBox)
        topHBox.addLayout(operationVBox)
        topWidget = QWidget(self)
        topWidget.setLayout(topHBox)
        self.setCentralWidget(topWidget)

        '''
        status
        '''

        # moniter = QApplication.desktop().size()
        moniter = QApplication.primaryScreen().size()
        print('H: %s, W: %s' % (moniter.height(), moniter.width()))
        self.resize(int(moniter.width() / 1.2), int(moniter.height() / 1.2))
        self.move((moniter.width() - self.size().width()) / 2, (moniter.height() - self.size().height()) / 2)

        self.realScale = None

        '''
        actions
        '''
        # File Menu
        self.openImageAction = QAction(QIcon('./images/icons/open-folder.png'), 'Open image', self)
        self.openImageAction.triggered.connect(self.openFile)
        self.saveImageWithPolygonAction = QAction(QIcon('./images/icons/save.png'), 'Save image with polygon', self)
        self.saveImageWithPolygonAction.triggered.connect(self.saveImageWithPolygon)
        self.saveImageWithMaskAction = QAction(QIcon('./images/icons/export.png'), 'Save image with mask', self)
        self.saveImageWithMaskAction.triggered.connect(self.saveImageWithMask)
        self.closeAction = QAction(QIcon('./images/icons/close.png'), 'Close', self)
        self.closeAction.triggered.connect(self.closeImage)
        self.exitAction = QAction(QIcon('./images/icons/exit.png'), 'Exit', self)
        self.exitAction.triggered.connect(self.quit)
        # Edit Menu
        self.setRealScaleAction = QAction(QIcon('./images/icons/Ruler.png'), 'Set Real Scale', self)
        self.setRealScaleAction.triggered.connect(self.setRealScale)
        self.imageCropAction = QAction(QIcon('./images/icons/crop.png'), 'Crop the origin image', self)
        self.imageCropAction.triggered.connect(self.cropImage)
        self.drawPolygonAction = QAction(QIcon('./images/icons/polygon.png'), 'Create a new polygon on origin image',
                                         self)
        self.drawPolygonAction.triggered.connect(self.drawPolygon)
        self.deleteSelectedPolygonAction = QAction(QIcon('./images/icons/delete-new.png'), 'Delete selected polygon',
                                                   self)
        self.deleteSelectedPolygonAction.triggered.connect(self.deleteSelectedPolygon)
        self.deleteAllPolygonsAndResultsAction = QAction(QIcon('./images/icons/delete.png'),
                                                         'Delete all polygon and results')
        # self.deleteAllPolygonsAndResultsAction.triggered.connect()
        # Analysis Menu
        self.analysisAction = QAction(QIcon('./images/icons/run.png'), 'Analysis', self)
        self.analysisAction.triggered.connect(self.analysis)
        self.removeSmallBlocksAction = QAction(QIcon('./images/icons/filter.png'), 'Remove small blocks', self)
        self.removeSmallBlocksAction.triggered.connect(self.removeSmallBlocks)
        self.removeSmallHoleSAction = QAction(QIcon('./images/icons/filter.png'), 'Remove small holes', self)
        self.removeSmallHoleSAction.triggered.connect(self.removeSmallHoles)
        self.showResultTableAction = QAction(QIcon('./images/icons/table.png'), 'Result Table', self)
        self.showResultTableAction.triggered.connect(self.showResultTable)
        # Help Menu
        self.documentAction = QAction(QIcon('./images/icons/book.png'), 'Totorial', self)
        self.documentAction.triggered.connect(self.totorial)
        self.infoAction = QAction(QIcon('./images/icons/info-circle.png'), 'Info', self)
        self.infoAction.triggered.connect(self.info)
        self.aboutAction = QAction(QIcon('./images/icons/question-circle.png'), 'About', self)
        self.aboutAction.triggered.connect(self.about)

        '''
        menu bar
        '''
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(self.openImageAction)
        saveMenu = fileMenu.addMenu('Save')
        saveMenu.addAction(self.saveImageWithPolygonAction)
        saveMenu.addAction(self.saveImageWithMaskAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.closeAction)
        fileMenu.addAction(self.exitAction)
        editMenu = menubar.addMenu('Edit')
        editMenu.addAction(self.setRealScaleAction)
        editMenu.addAction(self.imageCropAction)
        editMenu.addAction(self.drawPolygonAction)
        editMenu.addAction(self.deleteSelectedPolygonAction)
        editMenu.addAction(self.deleteSelectedPolygonAction)
        analysisMenu = menubar.addMenu('Analysis')
        analysisMenu.addAction(self.analysisAction)
        analysisMenu.addSeparator()
        analysisMenu.addAction(self.removeSmallBlocksAction)
        analysisMenu.addAction(self.removeSmallHoleSAction)
        analysisMenu.addSeparator()
        analysisMenu.addAction(self.showResultTableAction)
        helpMenu = menubar.addMenu('Help')
        helpMenu.addAction(self.documentAction)
        helpMenu.addAction(self.infoAction)
        helpMenu.addAction(self.aboutAction)

        '''
        action bar
        '''
        # file
        self.toolbar = self.addToolBar('File')
        self.toolbar.addAction(self.openImageAction)
        self.toolbar.addAction(self.saveImageWithPolygonAction)
        self.toolbar.addAction(self.saveImageWithMaskAction)
        self.toolbar.addAction(self.closeAction)
        self.toolbar.addSeparator()
        # edit
        self.toolbar.addAction(self.setRealScaleAction)
        self.toolbar.addAction(self.imageCropAction)
        self.toolbar.addAction(self.drawPolygonAction)
        self.toolbar.addAction(self.deleteSelectedPolygonAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.analysisAction)
        self.toolbar.addAction(self.removeSmallBlocksAction)
        self.toolbar.addAction(self.removeSmallHoleSAction)
        self.toolbar.addAction(self.showResultTableAction)
        # self.toolbar.addSeparator()
        # self.toolbar.addAction(self.documentAction)
        # self.toolbar.addAction(self.infoAction)
        # self.toolbar.addAction(self.aboutAction)

        # action status
        # self.saveImageWithPolygonAction.setDisabled(True)
        # self.saveImageWithMaskAction.setDisabled(True)
        # self.analysisAction.setDisabled(True)
        # self.deleteSelectedPolygonAction.setDisabled(True)
        '''
        status bar
        '''
        self.statusLabel = QLabel()
        # self.statusLabel.setFixedWidth(80)
        self.statusLabel.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.statusLabel.setText('X: 0, Y: 0')
        import datetime
        self.statusBarCopyright = QLabel('Copyright©2019-%s Dorad. All Rights Reserved. Email: cug_xia@cug.edu.cn' % (
            datetime.datetime.now().year))

        self.progressBar = QProgressBar()
        # progressBar.setHidden()
        self.progressBar.setRange(0, 100)
        self.progressBar.setVisible(False)
        self.statusBar().addWidget(self.statusLabel)
        self.statusBar().addWidget(self.progressBar)
        self.statusBar().addPermanentWidget(self.statusBarCopyright)
        '''
        signals
        '''

        def update_mouse_pos_on_status_bar(pos: QPointF):
            self.statusLabel.setText('X: %d, Y: %d' % (round(pos.x(), 0), round(pos.y(), 0)))

        self.originView.MousePosChangedSignal.connect(update_mouse_pos_on_status_bar)
        self.resultView.MousePosChangedSignal.connect(update_mouse_pos_on_status_bar)

        self.originView.PolygonDrawFinishedSignal.connect(self.updateActionState)
        self.originView.LineDrawFinishedSIgnal.connect(self.updateActionState)
        self.updateActionState()

    '''
    File Menu callback
    '''

    def openFile(self):
        filePath, fileType = QFileDialog.getOpenFileName(self, 'Choose the image', '',
                                                         'Image (*.jpg);;Image (*.png);;Image (*.tif)')
        if not filePath:
            QMessageBox.warning(self, 'No File Selected', 'No image file is selected.')
        else:
            self.originView.setImage(imagePath=filePath)
            self.resultView.setImage(imagePath=filePath)
        self.updateActionState()

    def saveImageWithPolygon(self):
        if not self.originView.Image:
            return
        image = self.originView.renderImage(remove_useless_background=True)
        if not image:
            return
        import datetime
        filePath, fileType = QFileDialog.getSaveFileName(self, 'Choose the path for image',
                                                         './ImageWithPolygon-%s.png' % (
                                                             datetime.datetime.now().strftime('%Y%d%m%H%M%S')),
                                                         'Image (*.png);;')
        if not filePath:
            QMessageBox.warning(self, 'No Path Selected', 'No Path is selected.')
        else:
            image.save(filePath)

    def saveImageWithMask(self):
        if not self.resultView.Image:
            return
        image = self.resultView.renderImage(remove_useless_background=True)
        if not image:
            return
        import datetime
        filePath, fileType = QFileDialog.getSaveFileName(self, 'Choose the path for image',
                                                         './ImageWithPolygon-%s.png' % (
                                                             datetime.datetime.now().strftime('%Y%d%m%H%M%S')),
                                                         'Image (*.png);;')
        if not filePath:
            QMessageBox.warning(self, 'No Path Selected', 'No Path is selected.')
        else:
            image.save(filePath)

    def closeImage(self):
        print('Close')
        reply = QMessageBox.warning(self, 'Warning', 'Are you sure to close the image?',
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.originView.initUi()
            self.resultView.initUi()

        self.updateActionState()

    def quit(self):
        self.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        reply = QMessageBox.warning(self, 'Exit', 'Exit the program?',
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    '''
    Edit Menu callback
    '''

    def setRealScale(self):
        self.originView.startDraw(mode='scaleLine')

        def scaleLineFinishedHandler(mode, line: QLineF):
            if not mode == 'scaleLine':
                return
            # show dialog for input the length of line
            lineLength, ok = QInputDialog.getDouble(self, 'Input the length of line', 'Length of line(mm)')
            if not ok:
                return
            if not (lineLength and line.length()):
                QMessageBox.warning('Length of line must be positive number.')
                return
            self.realScale = lineLength / line.length()
            print('Real Scale: %s' % self.realScale)

        self.originView.LineDrawFinishedSIgnal.connect(scaleLineFinishedHandler)
        self.updateActionState()

    def cropImage(self):
        # draw a polygon and make a mask for the image
        self.originView.startDraw(mode='cropPolygon')

        def cropPolygonFinishedHandler(mode, polygon: QPolygonF):
            if mode != 'cropPolygon':
                return
            # add polygon to originView and resultView
            self.originView.setCropPolygon(polygon)
            self.resultView.setCropPolygon(polygon)
            self.updateActionState()

        self.originView.PolygonDrawFinishedSignal.connect(cropPolygonFinishedHandler)

    def drawPolygon(self):
        self.originView.startDraw(mode='polygon')
        self.updateActionState()

    def deleteSelectedPolygon(self):
        self.originView.delPolygonSelected()
        self.updateActionState()

    '''
    Analysis Menu callback
    '''

    def analysis(self):
        # progressDialog.show()
        # msgBox=QMessageBox.information(self, 'Analysising', 'The result is being calculated, please wait. ')
        self.resultView.deleteAllLabels()
        progress = QProgressDialog(self)
        progress.setWindowTitle("Analyzing")
        progress.setLabelText("Analyzing...")
        progress.setCancelButtonText("cancel")
        progress.setMinimumDuration(5)
        progress.setWindowModality(Qt.WindowModal)
        progress.setRange(0, len(self.originView.PolygonList))
        for i, polygon in enumerate(self.originView.PolygonList):
            self.resultView.addPolygonArea(polygon['geo'])
            progress.setValue(i + 1)
        progress.close()
        QMessageBox.information(self, 'Finished', 'Analysis is Finished.')
        self.updateActionState()

    def removeSmallBlocks(self):
        # get the setting
        minBlockSizeVlue, ok = QInputDialog.getInt(self, 'Input the filter value', 'Miniumn size of block', 64, 0)
        if not ok:
            return
        self.resultView.removeSmallBlocks(minBlockSizeVlue)
        self.updateActionState()

    def removeSmallHoles(self):
        # get the setting
        minHoleValue, ok = QInputDialog.getInt(self, 'Input the filter value', 'Miniumn size of hole in block', 64, 0)
        if not ok:
            return
        self.resultView.removeSmallHoles(minHoleValue)
        self.updateActionState()

    def showResultTable(self):
        from ImageLabelDataTable import LabelDataTable
        self.resultTable = LabelDataTable()
        self.resultTable.setData(self.resultView.labelMask, self.realScale, self.originView.cropPolygon)
        self.resultTable.show()
        self.updateActionState()
        self.resultTable.labelSelectedSignal.connect(self.resultView.setShowLabelList)

    def totorial(self):
        QDesktopServices.openUrl(QUrl('https://blog.cuger.cn'))

    def info(self):
        msgBox = QMessageBox(QMessageBox.NoIcon, 'SFRM Tool',
                             'Shear Failure Regions of Rock Joints Measurement Tool is designed to detect shear failure region from discontinuity image which is taken after Direct Shear Test.')
        # QMessageBox.information(self, 'DSFRD Tool',
        #                         'Discontinuity Shear Failure Region Detection Tool is designed to detect shear failure region from discontinuity image which is taken after Direct Shear Test.')
        msgBox.setIconPixmap(QPixmap('./images/icons/logo.png'))
        msgBox.exec()

    def about(self):
        QMessageBox.information(self, 'About Us',
                                'SFRM Tool is designed to determine shear failure regions of rock joints based on image which is taken after Direct Shear Test.\r\n\r\n\r\nAuthor: Ding Xia\r\nEmail: cug.xia@gmail.com\r\nBlog: https://blog.cuger.cn\r\nCopyright © 2019-%s All Rights Reserved.' % (
                                    datetime.datetime.now().year))

    def updateActionState(self):
        '''
        update the state of the main window.
        '''
        # file
        ## save
        self.saveImageWithPolygonAction.setEnabled(self.originView.Image != None)
        self.saveImageWithMaskAction.setEnabled(self.resultView.Image != None)
        ## close
        self.closeAction.setEnabled(self.originView.Image != None)
        ## edit

        # edit
        self.setRealScaleAction.setEnabled(self.originView.Image != None)
        self.imageCropAction.setEnabled(self.originView.Image != None and self.originView.cropPolygon == None)
        self.drawPolygonAction.setEnabled(self.originView.Image != None and self.originView.cropPolygon != None)
        self.deleteSelectedPolygonAction.setEnabled(len(self.originView.PolygonList) > 0)

        # analysis
        self.analysisAction.setEnabled(len(self.originView.PolygonList) > 0)
        self.removeSmallBlocksAction.setEnabled(np.sum(self.resultView.labelMask) > 0)
        self.removeSmallHoleSAction.setEnabled(np.sum(self.resultView.labelMask) > 0)
        self.showResultTableAction.setEnabled(np.sum(self.resultView.labelMask) > 0)

        self.update()


import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    # imagePath = './res/SY4.JPG'
    # mainWindow.originView.setImage(imagePath)
    # mainWindow.originView.setImageCenter()
    mainWindow.show()
    sys.exit(app.exec_())
