import managers.managerDatalineSettings
import windows.windowLogger
import windows.windowDatalineWork


def getDatalineDescrList() -> list:
    datalineSettingsManager = managers.managerDatalineSettings.ManagerDatalineSettings(self.profileTitle)
    datalineList = datalineSettingsManager.getDatalineSettingsList()

    return datalineList


if __name__ == '__main__':
    profileTitle = "test_profile_serv"
    logger = windows.windowLogger.WindowLogger(profileTitle)
    logger.show()

    datalineParamsList = getDatalineDescrList()
    datalineDataDict = datalineParamsList[0]

    datalineWindow = windows.windowDatalineWork.WindowDatalineWork(profileTitle, datalineDataDict, logger)

    datalineWindow.signalToLoggerMsgReceived.connect(logger.addMsgReceived)
    datalineWindow.signalToLoggerMsgSent.connect(logger.addMsgSent)
    datalineWindow.signalToLoggerMsgError.connect(logger.addMsgError)