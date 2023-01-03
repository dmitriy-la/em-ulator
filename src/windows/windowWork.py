import gettext

from PyQt5.QtWidgets import QDialog

import managers.managerDatalineSettings
import windows.windowDatalineWork
import windows.windowLogger


_ = gettext.gettext


class WindowWork(QDialog):
    def __init__(self, profileTitle: str):
        super().__init__()
        self.datalineList = []

        self.profileTitle = profileTitle

        self.startLogger()

        self.startAllDataline()


    def startLogger(self):
        self.logger = windows.windowLogger.WindowLogger(self.profileTitle, self)
        self.logger.closeAppSignal.connect(self.appExit)
        self.logger.show()


    def getDatalineDescrList(self) -> list:
        datalineSettingsManager = managers.managerDatalineSettings.ManagerDatalineSettings(self.profileTitle)
        datalineList = datalineSettingsManager.getDatalineSettingsList()

        return datalineList


    def startAllDataline(self):
        datalineParamsList = self.getDatalineDescrList()

        for datalineDataDict in datalineParamsList:
            datalineWindow = windows.windowDatalineWork.WindowDatalineWork(self.profileTitle, datalineDataDict, self.logger)

            datalineWindow.signalToLoggerMsgReceived.connect(self.logger.addMsgReceived)
            datalineWindow.signalToLoggerMsgSent.connect(self.logger.addMsgSent)
            datalineWindow.signalToLoggerMsgError.connect(self.logger.addMsgError)

            self.datalineList.append(datalineWindow)


    def appExit(self):
        for dataline in self.datalineList:
            dataline.close()

        self.datalineList.clear()

        if self.sender() != self.logger:
            self.logger.close()

        self.close()


    def closeApp(self):
        for dataline in self.datalineList:
            dataline.close()

        self.datalineList.clear()

        self.logger.close()

        self.close()
