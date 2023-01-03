import gettext

from PyQt5.Qt import Qt
from PyQt5.QtCore import QPoint, QSettings, pyqtSignal, QSize, QRect, pyqtSlot
from PyQt5.QtWidgets import QSizeGrip, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QMainWindow
from PyQt5.QtGui import QFont, QIcon, QPixmap

import widgets.textEditWithClearing
import windows.windowLoggerSettings


_ = gettext.gettext


class WindowLogger(QWidget):
# class WindowLogger(QMainWindow):
    closeAppSignal = pyqtSignal()
    _gripSize = 8

    def __init__(self, profileTitle: str, parent=None):
        super().__init__()
        self.profileTitle = profileTitle
        self.parent = parent

        self.settings = QSettings()

        self.initUI()


    def readSettingsLogger(self):
        self.settings.beginGroup('/' + self.profileTitle)

        self.settings.beginGroup('/GraphicSettingsLogger')
        try:
            self.xCoord = int(self.settings.value('/Left'))
            self.yCoord = int(self.settings.value('/Right'))
            self.windowHeight = int(self.settings.value('/Height'))
            self.windowWidth = int(self.settings.value('/Width'))
        except TypeError:
            self.xCoord = 33
            self.yCoord = 33
            self.windowHeight = 600
            self.windowWidth = 640

        self.settings.endGroup()

        self.settings.endGroup()


    def initUI(self):
        self.setWindowProperties()

        self.layout = QHBoxLayout(self)

        self.addMainTextEdit()
        self.addVLayoutSideButtons()

        self.setLayout(self.layout)

        self.show()

        self.oldPos = QPoint(self.x(), self.y())

        self.oldGeometry = self.geometry()


    def setWindowProperties(self):
        self.setWindowTitle(_("Log"))

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.cornerGrips = [QSizeGrip(self) for _ in range(4)]

        self.xCoord = 33
        self.yCoord = 33
        self.windowHeight = 600
        self.windowWidth = 640
        self.readSettingsLogger()

        if self.xCoord is None:
            self.xCoord = 33
            self.yCoord = 33
            self.windowHeight = 600
            self.windowWidth = 640

        self.setGeometry(self.xCoord, self.yCoord, self.windowWidth, self.windowHeight)
        self.setMinimumWidth(400)


    def addVLayoutSideButtons(self):
        vLayoutSideButtons = QVBoxLayout(self)

        self.addButtonExit(vLayoutSideButtons)
        self.addButtonSettings(vLayoutSideButtons)

        vLayoutSideButtons.addStretch(1)

        self.layout.addLayout(vLayoutSideButtons)


    def addButtonExit(self, vLayoutSideButtons):
        self.buttonExit = QPushButton()

        pixmap = QPixmap('../icons/close1.png')
        closeIcon = QIcon(pixmap)
        self.buttonExit.setIcon(closeIcon)
        self.buttonExit.setIconSize(QSize(20, 20))

        self.buttonExit.clicked.connect(self.close)

        vLayoutSideButtons.addWidget(self.buttonExit)


    def addButtonSettings(self, vLayoutSideButtons):
        self.buttonSettings = QPushButton()

        pixmap = QPixmap('../icons/settings.png')
        closeIcon = QIcon(pixmap)
        self.buttonSettings.setIcon(closeIcon)
        self.buttonSettings.setIconSize(QSize(20, 20))

        self.buttonSettings.clicked.connect(self.showLoggerSettings)

        vLayoutSideButtons.addWidget(self.buttonSettings)


    def addMainTextEdit(self):
        self.textEdit = widgets.textEditWithClearing.TextEditWithClearing(self)
        self.textEdit.setReadOnly(True)

        font = QFont('Consolas', 10.5, QFont.Normal)
        self.textEdit.setFont(font)

        self.layout.addWidget(self.textEdit)


    def showLoggerSettings(self):
        win = windows.windowLoggerSettings.WindowLoggerSettings(self)


    def addMsgReceived(self, msg: str):
        self.textEdit.setTextColor(Qt.darkGreen)
        self.textEdit.append(msg)


    @pyqtSlot(str)
    def addMsgSent(self, msg: str):
        self.textEdit.setTextColor(Qt.black)
        self.textEdit.append(msg)


    def addMsgError(self, msg: str):
        self.textEdit.setTextColor(Qt.red)
        self.textEdit.append(msg)


    @property
    def gripSize(self):
        return self._gripSize


    def setGripSize(self, size):
        if size == self._gripSize:
            return
        self._gripSize = max(2, size)
        self.updateGrips()


    def updateGrips(self):
        outRect = self.rect()
        # an "inner" rect used for reference to set the geometries of size grips
        inRect = outRect.adjusted(self.gripSize, self.gripSize, -self.gripSize, -self.gripSize)

        # top left
        gripRectTopLeft = QRect(outRect.topLeft(), inRect.topLeft())
        self.cornerGrips[0].setGeometry(gripRectTopLeft)
        # top right
        gripRectTopRight = QRect(outRect.topRight(), inRect.topRight()).normalized()
        self.cornerGrips[1].setGeometry(gripRectTopRight)
        # bottom right
        gripRectBottomRight = QRect(inRect.bottomRight(), outRect.bottomRight())
        self.cornerGrips[2].setGeometry(gripRectBottomRight)
        # bottom left
        gripRectBottomLeft = QRect(outRect.bottomLeft(), inRect.bottomLeft()).normalized()
        self.cornerGrips[3].setGeometry(gripRectBottomLeft)


    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()


    def mouseMoveEvent(self, event):
        if self.oldGeometry != self.geometry():
            self.oldGeometry = self.geometry()
            return

        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()


    def resizeEvent(self, event):
        self.updateGrips()
        self.show()


    def closeEvent(self, event):
        self.writeSettingsLogger()

        print("Emitting close app")

        self.closeAppSignal.emit()


    def writeSettingsLogger(self):
        self.settings.beginGroup('/' + self.profileTitle)

        self.settings.beginGroup('/GraphicSettingsLogger')
        self.settings.setValue('/Left', int(self.x()))
        self.settings.setValue('/Right', int(self.y()))
        self.settings.setValue('/Height', int(self.height()))
        self.settings.setValue('/Width', int(self.width()))
        self.settings.endGroup()

        self.settings.endGroup()
