import gettext

from PyQt5.Qt import QSettings, QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QMessageBox, QPushButton

import src.managers.managerMsgFormats as managerMsgFormats
import src.managers.managerProfiles as managerProfiles


_ = gettext.gettext


class WindowProfiledWindow(QDialog):
    def __init__(self, profileTitle: str, parent=None):
        super().__init__(parent, Qt.Window)
        self.profileTitle = profileTitle

        self.parent = parent

        self.settings = QSettings()

        self.formatManager = managerMsgFormats.ManagerMsgFormats(self.profileTitle)
        self.listOfAllMsgTypesInfo = self.formatManager.getListOfAllMsgTypeDescrs()

        self.profileManager = managerProfiles.ManagerProfiles(self.profileTitle)
        self.maskForFormingReceiptType = self.profileManager.getMaskForFormingReceiptType()

        self.buttonClose = self.getCloseButton()
        self.buttonSave = self.getSaveButton()


    def getCloseButton(self) -> QPushButton:
        """
        :return:
        """
        buttonClose = QPushButton(self)
        buttonClose.setText(_('Close'))

        buttonClose.clicked.connect(self.close)

        pixmap = QPixmap('../icons/x.png')
        saveIcon = QIcon(pixmap)
        buttonClose.setIcon(saveIcon)
        buttonClose.setIconSize(QSize(11, 11))

        return buttonClose


    def getSaveButton(self) -> QPushButton:
        """
        :return:
        """
        buttonSaveMsgType = QPushButton(self)
        buttonSaveMsgType.setText(_('Save'))

        pixmap = QPixmap('../icons/save1.png')
        saveIcon = QIcon(pixmap)
        buttonSaveMsgType.setIcon(saveIcon)
        buttonSaveMsgType.setIconSize(QSize(13, 13))

        return buttonSaveMsgType


    def prepareMsg(self, msg) -> str:
        """

        :param msg:
        :return:
        """
        if isinstance(msg, bytes):
            msg = msg.decode('utf-8', 'replace')
        msg = msg.strip('b\'')
        msg = msg.replace('\'', '')

        return msg


    def showErrorMessageBox(self, errorText: str, errorSubtext=''):
        """
        :param errorText:
        :param errorSubtext:
        :return:
        """
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)

        msg.setWindowTitle(_("Error"))
        msg.setText(errorText)
        msg.setInformativeText(errorSubtext)

        # msg.setMinimumWidth(450)

        msg.adjustSize()

        msg.exec_()


    def showSuccessMessageBox(self, text: str, subtext='', title="Save"):
        """
        :param text:
        :param subtext:
        :return:
        """
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)

        msg.setWindowTitle(_(title))
        msg.setText(text)
        msg.setInformativeText(subtext)

        msg.setMinimumWidth(300)

        msg.exec_()
