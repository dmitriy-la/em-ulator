import src.managers.ioManager as ioManager


class ManagerDatalineSettings(ioManager.IoManager):
    def __init__(self, profileTitle='default'):
        super().__init__(profileTitle)

        self._dataListFilePath = './__profiles__/' + profileTitle + '/datalineSettings.json'
        self._dataList = self.readDataFromFile()


    def getDatalineSettingsByDatalineTitle(self, datalineTitle: str) -> dict:
        datalineDescr = self._getItemByValueInKey(datalineTitle, "title")

        return datalineDescr


    def updateDatalineSettingsOfSingleDataline(self, newDatalineDescr: dict) -> None:
        self._replaceItemInDataListByKey(newDatalineDescr, "title")
