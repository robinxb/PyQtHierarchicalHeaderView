#! /usr/bin/env python3
# -*- coding: cp1251 -*-
#
import sys
from PyQt4 import QtCore, QtGui
from ProxyModelWithHeaderModels import ProxyModelWithHeaderModels
from HierarchicalHeaderView import HierarchicalHeaderView

def BuildDataModel(model):
  cellText = "cell({0}, {1})"
  for i in range(4):
    l=[]
    for j in range(4):
      cell=QtGui.QStandardItem(cellText.format(i,j))
      l.append(cell);
    model.appendRow(l)

def BuildHeaderModel(headerModel):
  rootItem = QtGui.QStandardItem("root");
  rotatedTextCell=QtGui.QStandardItem("Rotated\n text");
  rotatedTextCell.setData(1, QtCore.Qt.UserRole);
  rootItem.appendColumn([rotatedTextCell]);
  cell=QtGui.QStandardItem("level 2");
  cell.appendColumn([QtGui.QStandardItem("level 3")]);
  cell.appendColumn([QtGui.QStandardItem("level 3")]);
  rootItem.appendColumn([cell])
  rootItem.appendColumn([QtGui.QStandardItem("level 2")]);
  headerModel.setItem(0, 0, rootItem);

app = QtGui.QApplication(sys.argv)
headerModel = QtGui.QStandardItemModel()
BuildHeaderModel(headerModel)
dataModel = QtGui.QStandardItemModel()
BuildDataModel(dataModel)

model=ProxyModelWithHeaderModels()
model.setModel(dataModel)
model.setHorizontalHeaderModel(headerModel)
model.setVerticalHeaderModel(headerModel)

tv = QtGui.QTableView()
tv.setHorizontalHeader(HierarchicalHeaderView(QtCore.Qt.Horizontal,tv));
tv.setVerticalHeader(HierarchicalHeaderView(QtCore.Qt.Vertical, tv));
tv.setModel(model)
tv.resizeColumnsToContents()
tv.resizeRowsToContents()
tv.show()

app.exec_()
