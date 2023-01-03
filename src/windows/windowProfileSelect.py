import sys
import os
import gettext
import configparser

from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSlot, QSize, QRect
from PyQt5.QtWidgets import QCheckBox, QComboBox, QDialog, QInputDialog, QMessageBox, QHBoxLayout, QPushButton, QVBoxLayout
from PyQt5.QtGui import QPixmap, QIcon

import windows.windowDatalineWork
import windows.windowLogger
import windows.windowProfileEditor
import managers.managerProfiles

_ = gettext.gettext


class WindowProfileSelect(QDialog):
    def __init__(self):
        super().__init__()

        self.initUI()

        self.datalineList = []


    def initUI(self) -> None:
        self.setWindowProperties()

        principalLayout = QVBoxLayout()

        self.addHBoxLayoutUpper(principalLayout)
        self.addVBoxLayoutLower(principalLayout)

        self.setLayout(principalLayout)


    def setWindowProperties(self) -> None:
        title = _('Profile manager')
        self.setWindowTitle(title)

        xCoord = 400
        yCoord = 200
        height = 130
        width = 218
        self.setGeometry(xCoord, yCoord, width, height)
        self.setMaximumHeight(height)

        # self.setFocusPolicy(Qt.StrongFocus)


    def addVBoxLayoutLower(self, hBoxLayout) -> None:
        vBoxLayoutLower = QVBoxLayout()

        vBoxLayoutLower.addStretch(1)

        self.checkBoxSetProfileAsDefault = QCheckBox(_('Set profile as default'), self)
        vBoxLayoutLower.addWidget(self.checkBoxSetProfileAsDefault)

        self.buttonStartWithSelectedProfile = QPushButton(_('Run with profile'), self)
        self.buttonStartWithSelectedProfile.clicked.connect(self.onClickStartWithProfile)
        pixmap = QPixmap('../icons/play.png')
        playIcon = QIcon(pixmap)
        self.buttonStartWithSelectedProfile.setIcon(playIcon)
        self.buttonStartWithSelectedProfile.setIconSize(QSize(15, 15))

        hLayButtonsStartWithAndExit = QHBoxLayout()
        hLayButtonsStartWithAndExit.addWidget(self.buttonStartWithSelectedProfile)
        self.addButtonExit(hLayButtonsStartWithAndExit)

        vBoxLayoutLower.addLayout(hLayButtonsStartWithAndExit)

        hBoxLayout.addLayout(vBoxLayoutLower)


    def addComboBoxListWithProfiles(self)-> QComboBox:
        self.comboBoxListWithProfiles = QComboBox()

        self.updateListOfProfiles()
        self.comboBoxListWithProfiles.currentTextChanged.connect(self.onSelectedProfileChanged)
        self.comboBoxListWithProfiles.setFixedHeight(21)
        self.comboBoxListWithProfiles.setToolTip("Select profile to edit or start with")

        return self.comboBoxListWithProfiles


    def updateListOfProfiles(self) -> None:
        self.comboBoxListWithProfiles.clear()

        profileTitlesList = self.getListOfAvailableProfiles()
        self.comboBoxListWithProfiles.addItem('')
        self.comboBoxListWithProfiles.addItems(profileTitlesList)


    def addHBoxLayoutUpper(self, hBoxLayout) -> None:
        hBoxLayoutUpper = QHBoxLayout()

        self.addButtonCreateProfile(hBoxLayoutUpper)
        self.comboBoxListWithProfiles = self.addComboBoxListWithProfiles()
        hBoxLayoutUpper.addWidget(self.comboBoxListWithProfiles)
        self.buttonEditProfile = self.addButtonEditProfile(hBoxLayoutUpper)
        self.buttonRemoveProfile = self.addButtonRemoveProfile(hBoxLayoutUpper)

        hBoxLayout.addLayout(hBoxLayoutUpper)


    def addButtonCreateProfile(self, vBoxLayoutRight) -> None:
        buttonCreateProfile = QPushButton()
        buttonCreateProfile.setToolTip(_('Create new emulator profile'))
        buttonCreateProfile.clicked.connect(self.onClickCreateProfile)

        pixmap = QPixmap('../icons/add-document.png')
        playIcon = QIcon(pixmap)
        buttonCreateProfile.setIcon(playIcon)
        buttonCreateProfile.setIconSize(QSize(15, 15))
        buttonCreateProfile.setMaximumWidth(25)

        vBoxLayoutRight.addWidget(buttonCreateProfile)


    def addButtonEditProfile(self, vBoxLayoutRight) -> QPushButton:
        buttonEditProfile = QPushButton()
        buttonEditProfile.clicked.connect(self.onClickEditProfile)
        buttonEditProfile.setEnabled(False)

        pixmap = QPixmap('../icons/edit.png')
        editIcon = QIcon(pixmap)
        buttonEditProfile.setIcon(editIcon)
        buttonEditProfile.setIconSize(QSize(15, 15))
        buttonEditProfile.setMaximumWidth(25)

        buttonEditProfile.setToolTip(_('Edit selected emulator profile'))

        vBoxLayoutRight.addWidget(buttonEditProfile)

        return buttonEditProfile


    def addButtonRemoveProfile(self, vBoxLayoutRight) -> QPushButton:
        buttonRemoveProfile = QPushButton()
        buttonRemoveProfile.setToolTip(_('Remove emulator profile'))
        buttonRemoveProfile.clicked.connect(self.onClickremoveProfile)
        buttonRemoveProfile.setEnabled(False)

        pixmap = QPixmap('../icons/trash.png')
        trashIcon = QIcon(pixmap)
        buttonRemoveProfile.setIcon(trashIcon)
        buttonRemoveProfile.setIconSize(QSize(15, 15))

        buttonRemoveProfile.setMaximumWidth(25)

        vBoxLayoutRight.addWidget(buttonRemoveProfile)

        return buttonRemoveProfile


    def addButtonExit(self, vBoxLayoutRight) -> None:
        buttonExit = QPushButton(_('Exit'), self)

        pixmap = QPixmap('../icons/x.png')
        saveIcon = QIcon(pixmap)
        buttonExit.setIcon(saveIcon)
        buttonExit.setIconSize(QSize(15, 15))

        buttonExit.clicked.connect(self.onClickExit)

        vBoxLayoutRight.addWidget(buttonExit)


    def getListOfAvailableProfiles(self) -> list:
        dir = './__profiles__/'
        listOfProfileFiles = []

        try:
            listOfProfileFiles = os.listdir(dir)
        except IOError:
            os.mkdir(dir)

        return listOfProfileFiles


    def getProfileTitleFromUser(self) -> str:
        profileTitle = ""

        while profileTitle == "":
            text, ok = QInputDialog.getText(self, _('Profile title'), _('Enter profile title:'))

            profileTitle = str(text)

            if not ok:
                break
            elif profileTitle == "":
                self.showErrorMessageBox(_("Empty profile title!"))
            else:
                profileManager = managers.managerProfiles.ManagerProfiles()
                profileManager.addEmptyProfile(profileTitle)

        return profileTitle


    @pyqtSlot()
    def onClickStartWithProfile(self) -> None:
        profileTitle = self.comboBoxListWithProfiles.currentText()
        print('Starting with profile', profileTitle)

        self.startProfile(profileTitle)

        self.close()


    def startProfile(self, profileTitle):
        self.logger = windows.windowLogger.WindowLogger(profileTitle)
        self.startAllDataline(profileTitle)

        if self.checkBoxSetProfileAsDefault.isChecked():
            self.setProfileAsDefault(profileTitle)


    def startAllDataline(self, profileTitle: str):
        datalineSettingsList = self.getDatalineDescrList(profileTitle)

        for index, datalineSettings in enumerate(datalineSettingsList):
            datalineWindow = windows.windowDatalineWork.WindowDatalineWork(profileTitle, datalineSettings, self.logger)

            datalineWindow.signalToLoggerMsgReceived.connect(self.logger.addMsgReceived)
            datalineWindow.signalToLoggerMsgSent.connect(self.logger.addMsgSent)
            datalineWindow.signalToLoggerMsgError.connect(self.logger.addMsgError)
            self.logger.closeAppSignal.connect(datalineWindow.close)

            self.datalineList.append(datalineWindow)


    def getDatalineDescrList(self, profileTitle: str) -> list:
        datalineSettingsManager = managers.managerDatalineSettings.ManagerDatalineSettings(profileTitle)
        datalineList = datalineSettingsManager.getDatalineSettingsList()

        return datalineList


    def setProfileAsDefault(self, selectedProfile: str) -> None:
        config = configparser.ConfigParser()
        try:
            with open('settings.ini', 'w+') as configFile:
                config.add_section('current_profile')
                config.set('current_profile', 'profile_title', selectedProfile)
                config.write(configFile)
        except IOError:
            print('Error setting up default profile')


    @pyqtSlot()
    def onClickCreateProfile(self) -> None:
        profileTitle = self.getProfileTitleFromUser()

        if profileTitle != "":
            self.comboBoxListWithProfiles.addItem(profileTitle)
            self.configImitProfile = windows.windowProfileEditor.WindowProfileEditor(profileTitle)


    @pyqtSlot()
    def onSelectedProfileChanged(self) -> None:
        if self.comboBoxListWithProfiles.currentText() == '':
            self.buttonEditProfile.setEnabled(False)
            self.buttonRemoveProfile.setEnabled(False)
            self.buttonStartWithSelectedProfile.setEnabled(False)
        else:
            self.buttonEditProfile.setEnabled(True)
            self.buttonRemoveProfile.setEnabled(True)
            self.buttonStartWithSelectedProfile.setEnabled(True)


    @pyqtSlot()
    def onClickEditProfile(self) -> None:
        currenttProfileTitle = self.comboBoxListWithProfiles.currentText()

        if currenttProfileTitle == '':
            return

        self.configImitProfile = windows.windowProfileEditor.WindowProfileEditor(currenttProfileTitle)


    @pyqtSlot()
    def onClickremoveProfile(self) -> None:
        profileTitleToRemove = self.comboBoxListWithProfiles.currentText()

        if profileTitleToRemove == '':
            return

        profileManager = managers.managerProfiles.ManagerProfiles(profileTitleToRemove)
        profileManager.removeProfile(profileTitleToRemove)

        profileTitleIndexInComboBox = self.comboBoxListWithProfiles.currentIndex()
        self.comboBoxListWithProfiles.removeItem(profileTitleIndexInComboBox)
        self.comboBoxListWithProfiles.currentIndex = 0


    def showErrorMessageBox(self, errorText: str, errorSubtext='') -> None:
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

        msg.exec_()


    def focusInEvent(self, event) -> None:
        self.updateListOfProfiles()


    @pyqtSlot()
    def onClickExit(self) -> None:
        sys.exit()
