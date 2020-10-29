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
import scipy.sparse as sp

from PyQt5.QtCore import QPointF, QLineF, Qt, QUrl
from PyQt5.QtGui import QIcon, QPolygonF, QDesktopServices, QPixmap, QCloseEvent, QKeySequence
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication, QAction, QLabel, QProgressBar, QFileDialog, \
    QMessageBox, QInputDialog, QMainWindow, QProgressDialog

from ImageViewerWithLabel import ImageViewerWithLabel
from ImageViewerWithPolygon import ImageViewerWithPolygon
import datetime
import json


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

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
        actions
        '''
        # Project Menu
        self.projectNewAction = QAction(QIcon('./images/icons/folder-open.png'), 'New project', self)
        self.projectNewAction.triggered.connect(self.newProject)
        self.openProjectAction = QAction(QIcon('./images/icons/folder-open.png'), 'Open project', self)
        self.openProjectAction.setShortcut(QKeySequence.Open)
        self.openProjectAction.triggered.connect(self.openProject)
        self.saveProjectAction = QAction(QIcon('./images/icons/save.png'), 'Save project', self)
        self.saveProjectAction.setShortcut(QKeySequence.Save)
        self.saveProjectAction.triggered.connect(self.saveProject)
        self.saveProjectAsAction = QAction(QIcon('./images/icons/save.png'), 'Save project as..', self)
        self.saveProjectAsAction.triggered.connect(self.saveProjectAs)

        # File Menu
        self.openImageAction = QAction(QIcon('./images/icons/load-image.png'), 'Open image', self)
        self.openImageAction.triggered.connect(self.openFile)
        self.saveImageWithPolygonAction = QAction(QIcon('./images/icons/save-polygon.png'), 'Save image with polygon',
                                                  self)
        self.saveImageWithPolygonAction.triggered.connect(self.saveImageWithPolygon)
        self.saveImageWithMaskAction = QAction(QIcon('./images/icons/save-mask.png'), 'Save image with mask', self)
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
        self.removeSmallBlocksAction = QAction(QIcon('./images/icons/filter-S.png'), 'Remove small regions', self)
        self.removeSmallBlocksAction.triggered.connect(self.removeSmallBlocks)
        self.removeSmallHoleSAction = QAction(QIcon('./images/icons/filter-H.png'), 'Remove small holes', self)
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
        self.aboutQtAction = QAction('About Qt', self)
        self.aboutQtAction.triggered.connect(self.aboutQt)

        '''
        menu bar
        '''
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(self.openImageAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.openProjectAction)
        fileMenu.addAction(self.saveProjectAction)
        fileMenu.addAction(self.saveProjectAsAction)
        fileMenu.addSeparator()
        saveMenu = fileMenu.addMenu('Export')
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
        helpMenu.addAction(self.aboutQtAction)

        '''
        action bar
        '''
        # file
        self.toolbar = self.addToolBar('File')
        self.toolbar.addAction(self.openImageAction)
        self.toolbar.addAction(self.openProjectAction)
        self.toolbar.addAction(self.saveProjectAction)
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
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.saveImageWithPolygonAction)
        self.toolbar.addAction(self.saveImageWithMaskAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.aboutAction)

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

        self.originView.PolygonDrawFinishedSignal.connect(self.__updateActionState)
        self.originView.LineDrawFinishedSIgnal.connect(self.__updateActionState)

        self.originView.ViewPointChangeSignal.connect(self.syncViewPoint)
        self.resultView.ViewPointChangeSignal.connect(self.syncViewPoint)
        self.initUi()

    def initUi(self):
        self.imagePath = None
        self.projectPath = None

        self.realScale = None

        '''
        status
        '''
        # moniter = QApplication.desktop().size()
        moniter = QApplication.primaryScreen().size()
        print('H: %s, W: %s' % (moniter.height(), moniter.width()))

        self.resize(int(moniter.width() / 1.2), int(moniter.height() / 1.2))
        self.move((moniter.width() - self.size().width()) / 2, (moniter.height() - self.size().height()) / 2)

        self.__updateActionState()

    '''
    File Menu callback
    '''

    def newProject(self):
        self.initUi()

    def openProject(self):
        filePath, fileType = QFileDialog.getOpenFileName(self, 'Choose the project file', filter=' project (*.pro);')
        if not filePath:
            QMessageBox.warning(self, 'No Project File Selected', 'No project file is selected.')
            return
        try:
            with open(filePath, 'r') as f:
                project = json.load(f)
            # decode
            self.initUi()
            project = JsonDecoding(project)
            self.imagePath = project['base_image']
            self.originView.setImage(imagePath=self.imagePath)
            self.originView.cropPolygon = project['crop_polygon']
            self.originView.polygonList = project['polygon']
            self.originView.setViewPoint(scale=project['scale'], offset=project['offset'])
            if 'real_scale' in project:
                self.realScale = project['real_scale']
            
            self.resultView.setImage(imagePath=self.imagePath)
            self.resultView.cropPolygon = project['crop_polygon']
            self.resultView.setViewPoint(scale=project['scale'], offset=project['offset'])
            self.resultView.addLabelMask(project['label_image'])
            self.projectPath = filePath
            self.__updateActionState()
        except Exception as e:
            QMessageBox.warning(self, 'Illegal Project Document',
                                'Illegal project document, please select a legal one.')
            return

    def saveProject(self):
        if self.projectPath is None:
            self.saveProjectAs()
        else:
            self.__saveProject()

    def saveProjectAs(self):
        filePath, fileType = QFileDialog.getSaveFileName(self, 'Choose the path for project',
                                                         'project-%s.pro' % (
                                                             datetime.datetime.now().strftime('%Y%m%d%H%M%S')),
                                                         ' project (*.pro);;')
        if not filePath:
            QMessageBox.warning(self, 'No Path Selected', 'No Path is selected.')
            return
        self.projectPath = filePath
        self.__saveProject()

    def openFile(self):
        filePath, fileType = QFileDialog.getOpenFileName(self, caption='Choose the image',
                                                         filter='Image (*.jpg);;Image (*.png);;Image (*.tif)')
        if not filePath:
            QMessageBox.warning(self, 'No File Selected', 'No image file is selected.')
        else:
            self.initUi()
            self.imagePath = filePath
            self.originView.setImage(imagePath=filePath)
            self.resultView.setImage(imagePath=filePath)
        self.__updateActionState()

    def saveImageWithPolygon(self):
        if not self.originView.Image:
            return
        image = self.originView.renderImage(remove_useless_background=True)
        if not image:
            return
        filePath, fileType = QFileDialog.getSaveFileName(self, 'Choose the path for image',
                                                         'ImageWithPolygon-%s.png' % (
                                                             datetime.datetime.now().strftime('%Y%m%d%H%M%S')),
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
                                                         'ImageWithPolygon-%s.png' % (
                                                             datetime.datetime.now().strftime('%Y%m%d%H%M%S')),
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

        self.__updateActionState()

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

    def syncViewPoint(self, oldOffset, newOffset, oldScal, newScale):
        self.originView.setViewPoint(newOffset, newScale)
        self.resultView.setViewPoint(newOffset, newScale)
        self.__updateActionState()

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
        self.__updateActionState()

    def cropImage(self):
        # draw a polygon and make a mask for the image
        self.originView.startDraw(mode='cropPolygon')

        def cropPolygonFinishedHandler(mode, polygon: QPolygonF):
            if mode != 'cropPolygon':
                return
            # add polygon to originView and resultView
            self.originView.setCropPolygon(polygon)
            self.resultView.setCropPolygon(polygon)
            self.__updateActionState()

        self.originView.PolygonDrawFinishedSignal.connect(cropPolygonFinishedHandler)

    def drawPolygon(self):
        self.originView.startDraw(mode='polygon')
        self.__updateActionState()

    def deleteSelectedPolygon(self):
        self.originView.delPolygonSelected()
        self.__updateActionState()

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
        progress.setRange(0, len(self.originView.polygonList))
        for i, polygon in enumerate(self.originView.polygonList):
            self.resultView.addPolygonArea(polygon['geo'])
            progress.setValue(i + 1)
        progress.close()
        QMessageBox.information(self, 'Finished', 'Analysis is Finished.')
        self.__updateActionState()

    def removeSmallBlocks(self):
        # get the setting
        minBlockSizeVlue, ok = QInputDialog.getInt(self, 'Input the filter value', 'Miniumn size of block', 64, 0)
        if not ok:
            return
        self.resultView.removeSmallBlocks(minBlockSizeVlue)
        self.__updateActionState()

    def removeSmallHoles(self):
        # get the setting
        minHoleValue, ok = QInputDialog.getInt(self, 'Input the filter value', 'Miniumn size of hole in block', 64, 0)
        if not ok:
            return
        self.resultView.removeSmallHoles(minHoleValue)
        self.__updateActionState()

    def showResultTable(self):
        from ImageLabelDataTable import LabelDataTable
        self.resultTable = LabelDataTable()
        self.resultTable.setData(self.resultView.labelMask, self.realScale, self.originView.cropPolygon)
        self.resultTable.show()
        self.__updateActionState()
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
        QMessageBox.about(self, 'About Us',
                          'SFRM Tool is designed to determine shear failure regions of rock joints based on image which is taken after Direct Shear Test.\r\n\r\n\r\nAuthor: Ding Xia\r\nEmail: cug.xia@gmail.com\r\nBlog: https://blog.cuger.cn\r\nCopyright © 2019-%s All Rights Reserved.' % (
                              datetime.datetime.now().year))
        # QMessageBox.information(self, 'About Us',
        #                         'SFRM Tool is designed to determine shear failure regions of rock joints based on image which is taken after Direct Shear Test.\r\n\r\n\r\nAuthor: Ding Xia\r\nEmail: cug.xia@gmail.com\r\nBlog: https://blog.cuger.cn\r\nCopyright © 2019-%s All Rights Reserved.' % (
        #                             datetime.datetime.now().year))

    def __updateActionState(self):
        '''
        update the state of the main window.
        '''
        # project
        self.saveProjectAction.setEnabled(self.imagePath is not None)
        self.saveProjectAsAction.setEnabled(self.imagePath is not None)
        # file

        ## save
        self.saveImageWithPolygonAction.setEnabled(self.originView.Image is not None)
        self.saveImageWithMaskAction.setEnabled(self.resultView.Image is not None)

        ## close
        self.closeAction.setEnabled(self.originView.Image is not None)

        ## edit

        # edit
        self.setRealScaleAction.setEnabled(self.originView.Image is not None)
        # self.imageCropAction.setEnabled(self.originView.Image is not None and self.originView.cropPolygon is None)
        self.imageCropAction.setEnabled(self.originView.Image is not None)
        self.drawPolygonAction.setEnabled(self.originView.Image is not None and self.originView.cropPolygon is not None)
        self.deleteSelectedPolygonAction.setEnabled(len(self.originView.polygonList) > 0)

        # analysis
        self.analysisAction.setEnabled(len(self.originView.polygonList) > 0)
        self.removeSmallBlocksAction.setEnabled(np.sum(self.resultView.labelMask) > 0)
        self.removeSmallHoleSAction.setEnabled(np.sum(self.resultView.labelMask) > 0)
        self.showResultTableAction.setEnabled(np.sum(self.resultView.labelMask) > 0)

        self.update()

    def aboutQt(self):
        QMessageBox.aboutQt(self)

    def __saveProject(self):
        if not self.projectPath:
            QMessageBox.warning(self, 'Error', 'No project file selected.')
            return
        project = {
            'name': '',
            'base_image': self.imagePath,
            'crop_polygon': self.originView.cropPolygon,
            'polygon': self.originView.polygonList,
            'offset': self.originView.offset,
            'scale': self.originView.scale,
            'real_scale': self.realScale,
            'label_image': self.resultView.labelMask
        }
        filePath = self.projectPath
        try:
            with open(filePath, mode='w+', encoding='utf-8') as f:
                json.dump(project, f, cls=JsonEncoding)
                QMessageBox.information(self, 'Success', 'Project file has been created successfully.')
        except Exception as e:
            QMessageBox.warning(self, 'Error', 'Failed to write project file.')
            return


class JsonEncoding(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QPolygonF):
            L = []
            for p in obj:
                L.append([p.x(), p.y()])
            return L
        elif isinstance(obj, QPointF):
            return [
                obj.x(),
                obj.y()
            ]
        elif isinstance(obj, np.ndarray):
            A = sp.csr_matrix(obj)
            return {
                'data': A.data.tolist(),
                'indptr': A.indptr.tolist(),
                'indices': A.indices.tolist()
            }
        else:
            return super(JsonEncoding, self).default(obj)


def JsonDecoding(project):
    # crop_polygon, QPolygonF
    T = QPolygonF()
    if project['crop_polygon']:
        for p in project['crop_polygon']:
            T.append(QPointF(p[0], p[1]))
    project['crop_polygon'] = T
    # polygon, QPolygon
    if project['polygon']:
        for polygon in project['polygon']:
            T = QPolygonF()
            for point in polygon['geo']:
                T.append(QPointF(point[0], point[1]))
            polygon['geo'] = T
    # label_image
    limage = project['label_image']
    project['offset'] = QPointF(project['offset'][0], project['offset'][1])
    if len(limage['data']):
        project['label_image'] = sp.csr_matrix((limage['data'], limage['indices'], limage['indptr']),
                                               dtype=int).toarray()
    else:
        project['label_image'] = np.array([])
    return project


import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    # imagePath = './res/SY4.JPG'
    # mainWindow.originView.setImage(imagePath)
    # mainWindow.originView.setImageCenter()
    mainWindow.show()
    sys.exit(app.exec_())
