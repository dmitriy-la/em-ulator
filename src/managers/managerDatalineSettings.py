import json
import os.path

import src.managers.ioManager as ioManager


class ManagerDatalineSettings(ioManager.IoManager):
    def __init__(self, profileTitle='default'):
        ioManager.IoManager.__init__(self)

        self.profileTitle = profileTitle

        self.datalineSettingsFilePath = './__profiles__/' + profileTitle + '/datalineSettings.json'

        self.datalineDescrsList = self.readDatalineSettingsList()


    def readDatalineSettingsList(self) -> list:
        datalineSettingsList = list()

        if os.path.exists(self.datalineSettingsFilePath):
            with open(self.datalineSettingsFilePath, 'r', newline='') as datalineListFile:
                datalineSettingsList = self.loadJsonFile(datalineListFile)
        else:
            with open(self.datalineSettingsFilePath, 'a+') as datalineListFile:
                self.dumpJsonFile(datalineListFile, datalineSettingsList)
                # json.dump(datalineSettingsList, datalineListFile, indent=4, ensure_ascii=False)

        self.datalineDescrsList = datalineSettingsList

        return datalineSettingsList


    def updateDatalineSettingsFile(self, datalineDescrsList: list) -> None:
        with open(self.datalineSettingsFilePath, 'w', newline='') as datalineListFile:
            self.dumpJsonFile(datalineListFile, datalineDescrsList)
            # json.dump(datalineDescrsList, datalineListFile, indent=4, ensure_ascii=False)


    def getDatalineSettingsList(self) -> list:
        return self.datalineDescrsList


    def getDatalineSettingsByDatalineTitle(self, datalineTitle: str) -> dict:
        for dataline in self.datalineDescrsList:
            if dataline["title"] == datalineTitle:
                return dataline


    def updateDatalineSettingsOfSingleDataline(self, newDatalineDescr: dict) -> None:
        for datalineIndex, dataline in enumerate(self.datalineDescrsList):
            if dataline["title"] == newDatalineDescr["title"]:
                self.datalineDescrsList.remove(dataline)
                self.datalineDescrsList.insert(datalineIndex, newDatalineDescr)

                self.updateDatalineSettingsFile(self.datalineDescrsList)
                break
