# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import qApp, QApplication, QMainWindow, QMessageBox, QProgressBar, QLabel, QGraphicsView
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter


class Viewer(QGraphicsView):
    progressSig = QtCore.pyqtSignal(str, int)
    zoomSig = QtCore.pyqtSignal()
    imageChangedSig = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)
        self.setDragMode(QGraphicsView.RubberBandDrag);
        self.currImage = None
        self.lastSceneItem = None
        self.scaleFactor = 1.0
        self.lastPos = None
        self.foregroundColor = QtCore.Qt.black
        self.backgroundColor = QtCore.Qt.white
        self.brushSize = 1
        self.panning = False
        self.drawing = False
        self.leftMode = "Zoom"

        # Set up graphics viewer
        # TODO: add a logo
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.lastPos = event.pos()
            self.panning = True
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            event.accept()
        elif event.button() == QtCore.Qt.LeftButton:
            if (self.leftMode == "Draw") or (self.leftMode == "Erase"):
                self.lastPos = event.pos()
                self.drawing = True
                self.setCursor(QtCore.Qt.CrossCursor)
                event.accept()
            else:
                QGraphicsView.mousePressEvent(self, event)
        else:
            QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.panning:
            delta = event.pos() - self.lastPos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.lastPos = event.pos()
            event.accept()
        elif self.drawing:
            painter = QPainter(self.currImage)
            if self.leftMode == "Draw":
                brushColor = self.foregroundColor
            else:
                brushColor = self.backgroundColor
            painter.setPen(QtGui.QPen(brushColor, self.brushSize, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
            painter.drawLine(self.mapToScene(self.lastPos), self.mapToScene(event.pos()))
            self.lastPos = event.pos()
            painter.end()

            # Update list widget with new image
            self.lastListItem.setData(QtCore.Qt.UserRole, self.currImage)

            # Replace current pixmap with new one
            self.currPixmap = QPixmap.fromImage(self.currImage)
            if self.lastSceneItem is not None:
                self.scene.removeItem(self.lastSceneItem)
            self.scene.addPixmap(self.currPixmap)
            self.lastSceneItem = self.scene.addPixmap(self.currPixmap)
            event.accept()
        else:
            QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.panning = False
            self.setCursor(QtCore.Qt.ArrowCursor)
            event.accept()
        elif event.button() == QtCore.Qt.LeftButton:
            if self.leftMode == "Zoom":
                topLeft = self.mapToScene(self.rubberBandRect().topLeft())
                bottomRight = self.mapToScene(self.rubberBandRect().bottomRight())
                self.fitInView(QtCore.QRectF(topLeft, bottomRight), QtCore.Qt.KeepAspectRatio)
                QGraphicsView.mouseReleaseEvent(self, event)
            elif self.leftMode == "Fill":
                # Find corners of area
                topLeft = self.mapToScene(self.rubberBandRect().topLeft())
                bottomRight = self.mapToScene(self.rubberBandRect().bottomRight())

                # Paint rectangle in background color
                painter = QPainter(self.currImage)
                painter.fillRect(QtCore.QRectF(topLeft, bottomRight), self.backgroundColor)
                painter.end()

                # Update list widget with new image
                self.lastListItem.setData(QtCore.Qt.UserRole, self.currImage)
                self.imageChangedSig.emit()

                # Replace current pixmap with new one
                self.currPixmap = QPixmap.fromImage(self.currImage)
                if self.lastSceneItem is not None:
                    self.scene.removeItem(self.lastSceneItem)
                self.scene.addPixmap(self.currPixmap)
                self.lastSceneItem = self.scene.addPixmap(self.currPixmap)
                QGraphicsView.mouseReleaseEvent(self, event)
            else:
                self.drawing = False
                self.setCursor(QtCore.Qt.ArrowCursor)
                self.imageChangedSig.emit()
                event.accept()
        else:
            QGraphicsView.mouseReleaseEvent(self, event)

    def imageSelected(self, curr, prev):
        if curr is not None:
            self.currImage = curr.data(QtCore.Qt.UserRole)
            pix = QPixmap.fromImage(self.currImage)
            if self.lastSceneItem is not None:
                self.scene.removeItem(self.lastSceneItem)
            self.scene.setSceneRect(-10.0, -10.0, pix.size().width() + 20.0, pix.size().height() + 20.0)
            self.lastSceneItem = self.scene.addPixmap(pix)
            self.fitToWindow()
        else:
            if self.lastSceneItem is not None:
                self.scene.removeItem(self.lastSceneItem)
                self.lastSceneItem = None
        self.lastListItem = curr

    def pointerMode(self):
        self.leftMode = "Zoom"
        self.setDragMode(QGraphicsView.RubberBandDrag);

    def pencilMode(self):
        self.leftMode = "Draw"
        self.setDragMode(QGraphicsView.NoDrag);

    def eraserMode(self):
        self.leftMode = "Erase"
        self.setDragMode(QGraphicsView.NoDrag);

    def areaFillMode(self):
        self.leftMode = "Fill"
        self.setDragMode(QGraphicsView.RubberBandDrag);

    def setBrush(self):
        whom = self.sender().objectName()
        if whom == "pix1Act":
            self.brushSize = 1
        elif whom == "pix4Act":
            self.brushSize = 4
        elif whom == "pix8Act":
            self.brushSize = 8
        else:
            self.brushSize = 12

    def zoomIn(self):
        if self.currImage is None:
            return
        self.scale(1.25, 1.25)
        self.scaleFactor = self.scaleFactor * 1.25
        self.zoomSig.emit()

    def zoomOut(self):
        if self.currImage is None:
            return
        self.scale(0.8, 0.8)
        self.scaleFactor = self.scaleFactor * 0.8
        self.zoomSig.emit()

    def zoomSelect(self):
        if self.currImage is None:
            return

    def fitToWindow(self):
        if self.currImage is None:
            return
        # Compute reference scale factor
        viewW = self.size().width()
        viewH = self.size().height()
        pixW = self.currImage.size().width() + 20
        pixH = self.currImage.size().height() + 20
        if (viewW * pixH > viewH * pixW):
            scale = 0.995 * viewH / pixH
        else:
            scale = 0.995 * viewW / pixW
        self.resetTransform()
        self.scale(scale, scale)
        self.scaleFactor = 1.0
        self.zoomSig.emit()

    def fitWidth(self):
        if self.currImage is None:
            return
        # Compute reference scale factor
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        viewW = self.size().width() - self.verticalScrollBar().width()
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        pixW = self.currImage.size().width() + 20
        scale = 0.995 * viewW / pixW
        self.resetTransform()
        self.scale(scale, scale)
        self.scaleFactor = 1.0
        self.zoomSig.emit()

    def fillWindow(self):
        if self.currImage is None:
            return
        # Compute reference scale factor
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        viewW = self.size().width() - self.verticalScrollBar().width()
        viewH = self.size().height() - self.horizontalScrollBar().height()
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        pixW = self.currImage.size().width() + 20
        pixH = self.currImage.size().height() + 20
        if (viewW * pixH > viewH * pixW):
            scale = 0.995 * viewW / pixW
        else:
            scale = 0.995 * viewH / pixH
        self.resetTransform()
        self.scale(scale, scale)
        self.scaleFactor = 1.0
        self.zoomSig.emit()