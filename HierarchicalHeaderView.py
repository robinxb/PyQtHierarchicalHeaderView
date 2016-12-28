#! /usr/bin/env python3
# -*- coding: cp1251 -*-
#
from PyQt4 import QtCore, QtGui

class private_data:
  def __init__(self):
    self.headerModel=None
  def initFromNewModel(self,orientation, model):
    self.headerModel = model.data(QtCore.QModelIndex(),(HierarchicalHeaderView.HorizontalHeaderDataRole if orientation==QtCore.Qt.Horizontal else HierarchicalHeaderView.VerticalHeaderDataRole))

  def findRootIndex(self,index):
    while index.parent().isValid() :
      index=index.parent()
    return index;

  def parentIndexes(self,index):
    indexes=[]
    while index.isValid():
      indexes.insert(0,index)
      index=index.parent()
    return indexes;

  def findLeaf(self,curentIndex,sectionIndex,curentLeafIndex):
    if curentIndex.isValid():
      childCount=curentIndex.model().columnCount(curentIndex)
      if childCount:
        for i in range(childCount):
          MI,curentLeafIndex = self.findLeaf(curentIndex.child(0, i), sectionIndex, curentLeafIndex)
          res = QtCore.QModelIndex(MI)
          if res.isValid():
            return res,curentLeafIndex
      else:
        curentLeafIndex+=1
        if curentLeafIndex==sectionIndex:
          return curentIndex,curentLeafIndex
    return QtCore.QModelIndex(),curentLeafIndex

  def leafIndex(self,sectionIndex):
    if self.headerModel:
      curentLeafIndex=-1
      for i in range(self.headerModel.columnCount()):
        MI,curentLeafIndex = self.findLeaf(self.headerModel.index(0, i), sectionIndex, curentLeafIndex)
        res = QtCore.QModelIndex(MI)
        if res.isValid():
          return res
    return QtCore.QModelIndex()
  def searchLeafs(self,curentIndex):
    res=[]
    if(curentIndex.isValid()):
      childCount=curentIndex.model().columnCount(curentIndex)
      if childCount:
        for i in range(childCount):
            res+=self.searchLeafs(curentIndex.child(0, i))
      else:
        res.append(curentIndex)
    return res


  def leafs(self,searchedIndex):
    leafs=[]
    if searchedIndex.isValid():
      childCount=searchedIndex.model().columnCount(searchedIndex)
      for i in range(childCount):
        leafs+=self.searchLeafs(searchedIndex.child(0, i))
    return leafs;


  def setForegroundBrush(self,opt,index):
    foregroundBrush=index.data(QtCore.Qt.ForegroundRole)
    if issubclass(foregroundBrush.__class__,QtGui.QBrush):
      opt.palette.setBrush(QtGui.QPalette.ButtonText,foregroundBrush)

  def setBackgroundBrush(self,opt, index):
    backgroundBrush = index.data(QtCore.Qt.BackgroundRole);
    if issubclass(backgroundBrush.__class__,QtGui.QBrush):
      opt.palette.setBrush(QtGui.QPalette.Button, backgroundBrush);
      opt.palette.setBrush(QtGui.QPalette.Window, backgroundBrush);

  def cellSize(self,leafIndex, hv, styleOptions):
    res = QtCore.QSize()
    vS = leafIndex.data(QtCore.Qt.SizeHintRole)
    if vS and issubclass(vS.__class__,QtCore.QSize):
      res=vS
    fnt = QtGui.QFont(hv.font());
    vF = leafIndex.data(QtCore.Qt.FontRole)
    if vF and issubclass(vF.__class__,QtGui.QFont):
      fnt=vF
    fnt.setBold(True);
    fm  = QtGui.QFontMetrics(fnt)
    size = QtCore.QSize(fm.size(0, str(leafIndex.data(QtCore.Qt.DisplayRole))))
    if leafIndex.data(QtCore.Qt.UserRole)!=None:
      size.transpose()
    decorationsSize = QtCore.QSize(hv.style().sizeFromContents(QtGui.QStyle.CT_HeaderSection, styleOptions, QtCore.QSize(), hv))
    emptyTextSize = QtCore.QSize(fm.size(0, ""))
    return res.expandedTo(size+decorationsSize-emptyTextSize)

  def currentCellWidth(self,searchedIndex, leafIndex, sectionIndex, hv):
    leafsList = self.leafs(searchedIndex)
    if len(leafsList)==0:
      return hv.sectionSize(sectionIndex);
    width=0
    firstLeafSectionIndex=sectionIndex-leafsList.index(leafIndex)
    for i in range(len(leafsList)):
      width+=hv.sectionSize(firstLeafSectionIndex+i);
    return width

  def currentCellLeft(self,searchedIndex, leafIndex, sectionIndex, left, hv):
    leafsList = self.leafs(searchedIndex)
    if len(leafsList)>0:
      n=leafsList.index(leafIndex)
      firstLeafSectionIndex=sectionIndex-n;
      n-=1;
      while n>=0:
        left-=hv.sectionSize(firstLeafSectionIndex+n)
        n-=1
    return left

  def paintHorizontalCell(self, painter, hv, cellIndex, leafIndex, logicalLeafIndex, styleOptions, sectionRect, top):
    uniopt = QtGui.QStyleOptionHeader(styleOptions)
    self.setForegroundBrush(uniopt, cellIndex)
    self.setBackgroundBrush(uniopt, cellIndex)
    height=self.cellSize(cellIndex, hv, uniopt).height()
    if cellIndex==leafIndex:
      height=sectionRect.height()-top;
    left=self.currentCellLeft(cellIndex, leafIndex, logicalLeafIndex, sectionRect.left(), hv);
    width=self.currentCellWidth(cellIndex, leafIndex, logicalLeafIndex, hv);

    r=QtCore.QRect(left, top, width, height);
    uniopt.text = str(cellIndex.data(QtCore.Qt.DisplayRole))
    painter.save()
    uniopt.rect = r;
    if cellIndex.data(QtCore.Qt.UserRole)!=None:
      hv.style().drawControl(QtGui.QStyle.CE_HeaderSection, uniopt, painter, hv)
      m=QtGui.QMatrix()
      m.rotate(-90)
      painter.setWorldMatrix(m, True)
      new_r = QtCore.QRect(0, 0,  r.height(), r.width())
      new_r.moveCenter(QtCore.QPoint(-r.center().y(), r.center().x()));
      uniopt.rect = new_r;
      hv.style().drawControl(QtGui.QStyle.CE_HeaderLabel, uniopt, painter, hv);
    else:
      hv.style().drawControl(QtGui.QStyle.CE_Header, uniopt, painter, hv)
    painter.restore()
    return top+height;

  def paintHorizontalSection(self,painter,sectionRect,logicalLeafIndex,hv,styleOptions,leafIndex):
    oldBO = QtCore.QPointF(painter.brushOrigin())
    top = sectionRect.y()
    indexes = self.parentIndexes(leafIndex)
    for i in range(len(indexes)):
      realStyleOptions = QtGui.QStyleOptionHeader(styleOptions)
      #if i<len(indexes)-1 and ( realStyleOptions.state.testFlag(QtGui.QStyle.State_Sunken) or realStyleOptions.state.testFlag(QtGui.QStyle.State_On)):
      #  t = QtGui.QStyle.State(QtGui.QStyle.State_Sunken | QtGui.QStyle.State_On);
      #  realStyleOptions.state&=(~t);
      top = self.paintHorizontalCell(painter, hv, indexes[i], leafIndex, logicalLeafIndex, realStyleOptions, sectionRect, top);
    painter.setBrushOrigin(oldBO);
  def paintVerticalCell(self,painter, hv, cellIndex, leafIndex, logicalLeafIndex, styleOptions, sectionRect, left):
            uniopt = QtGui.QStyleOptionHeader(styleOptions)
            self.setForegroundBrush(uniopt, cellIndex)
            self.setBackgroundBrush(uniopt, cellIndex)
            width=self.cellSize(cellIndex, hv, uniopt).width()
            if cellIndex==leafIndex:
                width=sectionRect.width()-left
            top=self.currentCellLeft(cellIndex, leafIndex, logicalLeafIndex, sectionRect.top(), hv)
            height=self.currentCellWidth(cellIndex, leafIndex, logicalLeafIndex, hv)
            r=QtCore.QRect(left, top, width, height)
            uniopt.text = str(cellIndex.data(QtCore.Qt.DisplayRole))
            painter.save()
            uniopt.rect = r;
            if cellIndex.data(QtCore.Qt.UserRole)!=None:
                hv.style().drawControl(QtGui.QStyle.CE_HeaderSection, uniopt, painter, hv)
                m=QtGui.QMatrix()
                m.rotate(-90)
                painter.setWorldMatrix(m, True);
                new_r=QtCore.QRect(0, 0,  r.height(), r.width())
                new_r.moveCenter(QtCore.QPoint(-r.center().y(), r.center().x()))
                uniopt.rect = new_r
                hv.style().drawControl(QtGui.QStyle.CE_HeaderLabel, uniopt, painter, hv)
            else:
                hv.style().drawControl(QtGui.QStyle.CE_Header, uniopt, painter, hv)
            painter.restore()
            return left+width

  def paintVerticalSection(self,painter, sectionRect, logicalLeafIndex, hv,styleOptions,leafIndex):
            oldBO=QtCore.QPointF(painter.brushOrigin())
            left=sectionRect.x();
            indexes = self.parentIndexes(leafIndex)
            for i in range(len(indexes)):
                realStyleOptions=QtGui.QStyleOptionHeader(styleOptions)
                #if(   i<indexes.size()-1
                #    &&
                #      (   realStyleOptions.state.testFlag(QStyle::State_Sunken)
                #       || realStyleOptions.state.testFlag(QStyle::State_On)))
                #{
                #    QStyle::State t(QStyle::State_Sunken | QStyle::State_On);
                #    realStyleOptions.state&=(~t);
                #}
                left=self.paintVerticalCell(painter, hv, indexes[i], leafIndex, logicalLeafIndex, realStyleOptions, sectionRect, left)
            painter.setBrushOrigin(oldBO);


class HierarchicalHeaderView(QtGui.QHeaderView):
  HorizontalHeaderDataRole=QtCore.Qt.UserRole
  VerticalHeaderDataRole=QtCore.Qt.UserRole+1

  def __init__(self,orientation,parent = None):
    QtGui.QHeaderView.__init__(self,orientation,parent)
    self._pd=private_data()
    #connect(this, SIGNAL(sectionResized(int, int, int)), this, SLOT(on_sectionResized(int)));
    self.connect(self, QtCore.SIGNAL("sectionResized(int, int, int)"), self.on_sectionResized)
  def styleOptionForCell(self,logicalInd):
    opt=QtGui.QStyleOptionHeader()
    self.initStyleOption(opt);
    if (self.window().isActiveWindow()):
        opt.state |= QtGui.QStyle.State_Active;
    opt.textAlignment = QtCore.Qt.AlignCenter;
    opt.iconAlignment = QtCore.Qt.AlignVCenter;
    opt.section = logicalInd
    visual = self.visualIndex(logicalInd);
    if self.count() == 1:
        opt.position = QtGui.QStyleOptionHeader.OnlyOneSection;
    else:
        if (visual == 0):
            opt.position = QtGui.QStyleOptionHeader.Beginning;
        else:
            opt.position=(QtGui.QStyleOptionHeader.End if visual==self.count()-1 else QtGui.QStyleOptionHeader.Middle);
    if self.isClickable():
      if self.highlightSections() and self.selectionModel():
        if self.orientation()==QtCore.Qt.Horizontal:
          if self.selectionModel().columnIntersectsSelection(logicalInd, self.rootIndex()):
            opt.state |= QtGui.QStyle.State_On;
          if self.selectionModel().isColumnSelected(logicalInd, self.rootIndex()):
            opt.state |= QtGui.QStyle.State_Sunken;
        else:
          if self.selectionModel().rowIntersectsSelection(logicalInd, self.rootIndex()):
            opt.state |= QtGui.QStyle.State_On;
          if self.selectionModel().isRowSelected(logicalInd, self.rootIndex()):
            opt.state |= QtGui.QStyle.State_Sunken;

    if self.selectionModel():
        previousSelected=False;
        if self.orientation()==QtCore.Qt.Horizontal:
            previousSelected = self.selectionModel().isColumnSelected(self.logicalIndex(visual - 1), self.rootIndex());
        else:
            previousSelected = self.selectionModel().isRowSelected(self.logicalIndex(visual - 1), self.rootIndex());
        nextSelected=False;
        if self.orientation()==QtCore.Qt.Horizontal:
            nextSelected = self.selectionModel().isColumnSelected(self.logicalIndex(visual + 1), self.rootIndex());
        else:
            nextSelected = self.selectionModel().isRowSelected(self.logicalIndex(visual + 1), self.rootIndex());
        if previousSelected and nextSelected:
            opt.selectedPosition = QtGui.QStyleOptionHeader.NextAndPreviousAreSelected;
        else:
            if previousSelected:
                opt.selectedPosition = QtGui.QStyleOptionHeader.PreviousIsSelected;
            else:
                if nextSelected:
                    opt.selectedPosition = QtGui.QStyleOptionHeader.NextIsSelected;
                else:
                    opt.selectedPosition = QtGui.QStyleOptionHeader.NotAdjacent;
    return opt;
    pass
  # protected??
  def paintSection(self,painter,rect,logicalIndex):
    if rect.isValid():
      leafIndex=QtCore.QModelIndex(self._pd.leafIndex(logicalIndex))
      if leafIndex.isValid():
        if(self.orientation() == QtCore.Qt.Horizontal):
          self._pd.paintHorizontalSection(painter, rect, logicalIndex, self, self.styleOptionForCell(logicalIndex), leafIndex);
        else:
          self._pd.paintVerticalSection(painter, rect, logicalIndex, self, self.styleOptionForCell(logicalIndex), leafIndex);
        return
    QtGui.QHeaderView.paintSection(self,painter, rect, logicalIndex);
  def sectionSizeFromContents(self,logicalIndex):
    if self._pd.headerModel:
      curLeafIndex = QtCore.QModelIndex(self._pd.leafIndex(logicalIndex));
      if curLeafIndex.isValid():
        styleOption = QtGui.QStyleOptionHeader(self.styleOptionForCell(logicalIndex));
        s=QtCore.QSize(self._pd.cellSize(curLeafIndex, self, styleOption));
        curLeafIndex=curLeafIndex.parent();
        while curLeafIndex.isValid():
          if self.orientation() == QtCore.Qt.Horizontal:
            s.setHeight(s.height()+self._pd.cellSize(curLeafIndex, self, styleOption).height())
          else:
            s.setWidth(s.width()+self._pd.cellSize(curLeafIndex, self, styleOption).width())
          curLeafIndex=curLeafIndex.parent();
        return s
    return QtGui.QHeaderView.sectionSizeFromContents(self,logicalIndex);

  def setModel(self,model):
    self._pd.initFromNewModel(self.orientation(), model);
    QtGui.QHeaderView.setModel(self,model)
    cnt=(model.columnCount() if self.orientation()==QtCore.Qt.Horizontal else model.rowCount())
    if cnt: self.initializeSections(0, cnt-1);
  # slot
  def on_sectionResized(self,logicalIndex):
    if self.isSectionHidden(logicalIndex): return;
    leafIndex = QtCore.QModelIndex(self._pd.leafIndex(logicalIndex));
    if leafIndex.isValid():
      leafsList = self._pd.leafs(self._pd.findRootIndex(leafIndex));
      for n in range(leafsList.index(leafIndex),1,-1): #(int n=leafsList.indexOf(leafIndex); n>0; --n)
        logicalIndex-=1;
        w = self.viewport().width()
        h = self.viewport().height()
        pos = self.sectionViewportPosition(logicalIndex)
        r=QtCore.QRect(pos, 0, w - pos, h)
        if self.orientation() == QtCore.Qt.Horizontal:
          if self.isRightToLeft(): r.setRect(0, 0, pos + self.sectionSize(logicalIndex), h);
        else:
            r.setRect(0, pos, w, h - pos);
        self.viewport().update(r.normalized());

