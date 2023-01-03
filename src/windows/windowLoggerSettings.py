import gettext
import os
from configparser import ConfigParser

from PyQt5.Qt import Qt
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QDialog, QCheckBox, QComboBox, QLabel, QPushButton, QHBoxLayout, QVBoxLayout

_ = gettext.gettext


class WindowLoggerSettings(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.initUI()


    def initUI(self):
        self.setWindowProperties()

        layout = QVBoxLayout(self)

        self.addComboBoxForSettingDefaultProfile(layout)
        self.addButtonEditProfile(layout)
        self.addButtonLoggerSettings(layout)
        self.addButtonTrackedMsgList(layout)

        layout.addStretch(1)

        self.setLayout(layout)

        self.show()


    def addComboBoxForSettingDefaultProfile(self, layout):
        self.comboBoxForSettingDefaultProfile = self.getComboBoxForSettingDefaultProfile()

        config = ConfigParser()
        try:
            with open('settings.ini', 'r') as configFile:
                config.read('settings.ini')
                currentDefaultProfile = config.get('current_profile', 'profile_title')
                self.comboBoxForSettingDefaultProfile.setCurrentText(currentDefaultProfile)
        except IOError:
            print('Settings file not found!')

        vLaySetCurrentProfile = QHBoxLayout()
        vLaySetCurrentProfile.addWidget(QLabel("Set default profile:"))
        vLaySetCurrentProfile.addWidget(self.comboBoxForSettingDefaultProfile)

        layout.addLayout(vLaySetCurrentProfile)


    def getComboBoxForSettingDefaultProfile(self):
        comboBoxForSettingDefaultProfile = QComboBox()

        profileTitlesList = self.getListOfAvailableProfiles()
        comboBoxForSettingDefaultProfile.addItem("")
        comboBoxForSettingDefaultProfile.addItems(profileTitlesList)

        return comboBoxForSettingDefaultProfile


    def getListOfAvailableProfiles(self) -> list:
        dir = './__profiles__/'
        listOfProfileFiles = []

        try:
            listOfProfileFiles = os.listdir(dir)
        except IOError:
            os.mkdir(dir)

        return listOfProfileFiles


    def setWindowProperties(self):
        self.setWindowTitle(_('Logger settings'))

        xCoord = 100
        yCoord = 133
        windowHeight = 100
        windowWidth = 200
        self.setGeometry(xCoord, yCoord, windowWidth, windowHeight)
        self.setMaximumWidth(200)
        self.setMaximumHeight(111)

        flags = self.windowFlags()
        self.setWindowFlags(int(flags) | Qt.Tool)

        self.oldPos = QPoint(self.x(), self.y())


    def addButtonTrackedMsgList(self, layout):
        self.buttonTrackedMsgList = QPushButton(_('Show monitor MSG log'))
        self.buttonTrackedMsgList.clicked.connect(self.showRememberedMsgList)

        self.buttonTrackedMsgList.setEnabled(False)

        layout.addWidget(self.buttonTrackedMsgList)


    def addButtonLoggerSettings(self, layout):
        self.buttonLoggerSettings = QPushButton(_('Logger settings'))

        self.buttonLoggerSettings.setEnabled(False)

        layout.addWidget(self.buttonLoggerSettings)


    def addButtonEditProfile(self, layout):
        self.buttonEditProfile = QPushButton(_('Edit profile'))
        self.buttonEditProfile.clicked.connect(self.showProfileSelect)

        self.buttonEditProfile.setEnabled(False)

        layout.addWidget(self.buttonEditProfile)


    def showProfileSelect(self):
        pass


    def showRememberedMsgList(self):
        pass


    def closeEvent(self, event):
        config = ConfigParser()

        try:
            with open('settings.ini', 'w+') as configFile:
                config.read('settings.ini')

                defaultProfileTitle = self.comboBoxForSettingDefaultProfile.currentText()

                if config.has_section('current_profile'):
                    config.set('current_profile', 'profile_title', defaultProfileTitle)
                else:
                    config.add_section('current_profile')
                    config.set('current_profile', 'profile_title', defaultProfileTitle)

                config.write(configFile)

        except IOError:
            print('Error while working with settings file.')
