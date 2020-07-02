#!/usr/bin/python3
# -*-coding:utf-8 -*-

# Reference: **********************************************
# @Project   : code
# @File    : ImageLabelDataTable.py
# @Time    : 2020/6/25 20:59
# @License   : LGPL
# @Author   : Dorad
# @Email    : cug.xia@gmail.com
# @Blog      : https://blog.cuger.cn

import csv

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QWidget, QToolBar, QAction, QTableWidget, QAbstractItemView, QVBoxLayout, QTableWidgetItem, \
    QFileDialog, QMessageBox, QApplication
import numpy as np


class LabelDataTable(QWidget):
    def __init__(self):
        super(LabelDataTable, self).__init__()

    def initUi(self):
        self.tableHeaders = [
            'Center X(px)', 'Center Y(px)', 'Area(mm^2)', 'Perimeter(mm)', 'Area(px^2)', 'Perimeter(px)'
        ]
        self.tableData = np.array([])

        # add action
        self.toolbar = QToolBar()
        self.saveAction = QAction(QIcon('./images/icons/save.png'), 'Export table as csv')
        self.saveAction.triggered.connect(self.saveAsCsv)
        self.toolbar.addAction(self.saveAction)

        self.table = QTableWidget(0, 6)  # id,area(mm^2), perimeter(mm), area(px^2), perimeter(px),cx(px),cy(px)
        self.table.setHorizontalHeaderLabels(self.tableHeaders)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setWindowTitle('Shear Failure Region Detection Result')
        self.setWindowIcon(QIcon('./images/icons/table-white.png'))
        self.table.verticalHeader().setVisible(True)
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.toolbar)
        self.mainLayout.addWidget(self.table)
        self.setLayout(self.mainLayout)
        self.labelData = []
        self.resize(self.table.size().width(), self.size().height())

    def setData(self, labelMask, realScale):
        self.initUi()
        from Image import imageLabelProperty
        self.labelData = imageLabelProperty(labelMask)
        self.tableData = np.zeros([len(self.labelData), 6])
        for i, row in enumerate(self.labelData):
            self.tableData[i, 0:6] = [
                row.centroid[0],
                row.centroid[1],
                row.area * realScale * realScale if realScale else 0,
                row.perimeter * realScale if realScale else 0,
                row.area,
                row.perimeter
            ]
        self.updateTable()

    def updateTable(self):
        self.table.setRowCount(len(self.labelData) + 1)
        for r in range(self.tableData.shape[0]):
            for c in range(self.tableData.shape[1]):
                item = QTableWidgetItem('%.2f' % self.tableData[r, c])
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.table.setItem(r, c, item)
        totalRow = len(self.tableData)
        item = QTableWidgetItem('Total')
        item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        item.setBackground(QColor(240, 240, 240))
        self.table.setItem(totalRow, 0, item)
        self.table.setSpan(totalRow, 0, 1, 2)
        for i in range(2, 6):
            item = QTableWidgetItem('%.2f' % np.sum(self.tableData[:, i]))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            item.setBackground(QColor(240, 240, 240))
            self.table.setItem(totalRow, i, item)
        self.update()

    def saveAsCsv(self):
        import datetime
        filePath, fileType = QFileDialog.getSaveFileName(self, 'Save File',
                                                         './ShearFailureRegion-%s.csv' % (
                                                             datetime.datetime.now().strftime('%Y%d%m%H%M%S')),
                                                         'CSV(*.csv)')
        if not filePath:
            QMessageBox.warning(self, 'No Path Selected', 'No Path is selected.')
        else:
            with open(filePath, 'w') as stream:
                writer = csv.writer(stream, lineterminator='\n')
                writer.writerow(self.tableHeaders)
                writer.writerows(list(self.tableData))
                writer.writerow([
                    'Total',
                    '',
                    self.table.item(self.table.rowCount() - 1, 2).text(),
                    self.table.item(self.table.rowCount() - 1, 3).text(),
                    self.table.item(self.table.rowCount() - 1, 4).text(),
                    self.table.item(self.table.rowCount() - 1, 5).text(),
                ])


if __name__ == '__main__':
    import numpy as np
    import sys

    app = QApplication(sys.argv)
    demo = LabelDataTable()
    labelMask = np.zeros([100, 100], int)
    labelMask[20:30, 10:30] = 1
    labelMask[50:60, 45:60] = 2
    labelMask[70:80, 35:80] = 3
    labelMask[10:15, 23:30] = 4
    labelMask[20:30, 50:70] = 5
    demo.setData(labelMask, 1)
    demo.show()
    sys.exit(app.exec_())
