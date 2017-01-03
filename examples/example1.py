#! /usr/bin/env python3
# -*- coding: cp1251 -*-
#
import sys
from PyQt4 import QtCore, QtGui
from PyQtHierarchicalHeaderView.PyQtHierarchicalHeaderView import PyQtHierarchicalHeaderView

class ExampleModel(QtCore.QAbstractTableModel):
  def __init__(self,parent=None):
    QtCore.QAbstractTableModel.__init__(self,parent)
    self._horizontalHeaderModel = QtGui.QStandardItemModel()
    self._verticalHeaderModel = QtGui.QStandardItemModel()
    self.fillHeaderModel(self._horizontalHeaderModel)
    self.fillHeaderModel(self._verticalHeaderModel)
  def fillHeaderModel(self,headerModel):
    rootItem = QtGui.QStandardItem("root");
    l=[]
    rotatedTextCell = QtGui.QStandardItem("Rotated text")
    rotatedTextCell.setData(1, QtCore.Qt.UserRole)
    l.append(rotatedTextCell)
    rootItem.appendColumn(l)

    cell=QtGui.QStandardItem("level 2");
    rootItem.appendColumn([cell]);

    cell.appendColumn([QtGui.QStandardItem("level 3")]);
    cell.appendColumn([QtGui.QStandardItem("level 3")]);
    rootItem.appendColumn([QtGui.QStandardItem("level 2")]);
    headerModel.setItem(0, 0, rootItem);

  def rowCount(self,parent):
    return 4

  def columnCount(self,parent):
    return 4

  def data(self,index,role):
    print()
    if role==PyQtHierarchicalHeaderView.HorizontalHeaderDataRole:
      return self._horizontalHeaderModel
    if role==PyQtHierarchicalHeaderView.VerticalHeaderDataRole:
      return self._verticalHeaderModel
    if(role==QtCore.Qt.DisplayRole and index.isValid()):
      return ("index({0}, {1})".format(index.row(),index.column()))
    return None


#/*    Qt::ItemFlags flags ( const QModelIndex & index ) const
#	{
#        return Qt::ItemIsEnabled | Qt::ItemIsSelectable;
#	}*/

app = QtGui.QApplication(sys.argv)
em = ExampleModel()
tv = QtGui.QTableView()
hv = PyQtHierarchicalHeaderView(QtCore.Qt.Horizontal, tv)
hv.setHighlightSections(True);
hv.setClickable(True);
tv.setHorizontalHeader(hv);

hv=PyQtHierarchicalHeaderView(QtCore.Qt.Vertical, tv)
hv.setHighlightSections(True)
hv.setClickable(True)
tv.setVerticalHeader(hv);
tv.setModel(em);

tv.resizeColumnsToContents()
tv.resizeRowsToContents()
tv.show()

app.exec_()

