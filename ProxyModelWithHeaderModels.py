#! /usr/bin/env python3
# -*- coding: cp1251 -*-
#
import sys
from PyQt4 import QtCore, QtGui, uic
from HierarchicalHeaderView import HierarchicalHeaderView

class ProxyModelWithHeaderModels(QtGui.QProxyModel):
  def __init__(self,parent=None):
    QtGui.QProxyModel.__init__(self,parent)
    self._horizontalHeaderModel=None
    self._verticalHeaderModel=None

  def data(self,index,role=QtCore.Qt.DisplayRole):
    if self._horizontalHeaderModel and role==HierarchicalHeaderView.HorizontalHeaderDataRole:
      return self._horizontalHeaderModel
    if self._verticalHeaderModel and role==HierarchicalHeaderView.VerticalHeaderDataRole:
      return self._verticalHeaderModel
    return QtGui.QProxyModel.data(self, index, role)

  def setHorizontalHeaderModel(self,headerModel):
    self._horizontalHeaderModel=headerModel
    cnt=self.model().columnCount()
    if cnt:
      self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, cnt-1)

  def setVerticalHeaderModel(self,headerModel):
    self._verticalHeaderModel=headerModel
    cnt=self.model().rowCount()
    if cnt:
      self.headerDataChanged.emit(QtCore.Qt.Vertical, 0, cnt-1)
