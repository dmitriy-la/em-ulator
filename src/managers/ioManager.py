import json
import os.path


class IoManager(object):
    def __init__(self, profileTitle: str):
        self.profileTitle = profileTitle

        self._dataList = []
        self._dataListFilePath = ''


    def readDataFromFile(self) -> list:
        self._dataList = self._readJsonFileByFilePath(self._dataListFilePath)

        return self._dataList


    def _readJsonFileByFilePath(self, datalineSettingsFilePath: str) -> list:
        datalineSettingsList = []

        if os.path.exists(datalineSettingsFilePath):
            datalineSettingsList = self._readDataFromFile(datalineSettingsFilePath)
        else:
            self._createEmptyFile(datalineSettingsFilePath)

        return datalineSettingsList


    def _readDataFromFile(self, filePath: str):
        try:
            with open(filePath, 'r', newline='') as file:
                dataList = json.load(file)
        except json.decoder.JSONDecodeError:
            dataList = self._createEmptyFile(filePath)

        return dataList


    def _createEmptyFile(self, filePath: str) -> list:
        with open(filePath, 'a+') as file:
            json.dump([], file, indent=4, ensure_ascii=False)

        return []


    def updateDataFile(self, dataList: list) -> None:
        self._dataList = dataList
        self._dumpDataToFile(dataList, self._dataListFilePath)


    def _dumpDataToFile(self, dataList: list, filePath: str) -> None:
        try:
            with open(filePath, 'w', newline='') as file:
                json.dump(dataList, file, indent=4, ensure_ascii=False)
        except IOError:
            print("IO error: Unable to update settings file!")


    def addItemToDataList(self, newItem: dict) -> None:
        self._dataList.append(newItem)
        self.updateDataFile(self._dataList)


    def _removeItemFromDataListByValueInKey(self, value: str, key: str) -> None:
        for item in self._dataList:
            if item[key] == value:
                self._dataList.remove(item)
                self.updateDataFile(self._dataList)
                break


    def _replaceItemInDataListByKey(self, newItem: dict, key: str) -> None:
        oldItem = self._getItemByValueInKey(newItem[key], key)

        try:
            itemIndex = self._dataList.index(oldItem)
            self._dataList.pop(itemIndex)
            self._dataList.insert(itemIndex, newItem)
        except ValueError:
            self.addItemToDataList(newItem)

        print("Datalist with replaced item:", self._dataList)

        self.updateDataFile(self._dataList)


    def getDataList(self) -> list:
        return self._dataList


    def _getListOfAllValuesInKey(self, key: str) -> list:
        allValuesInKey = self._getListOfAllValuesOfKeyInList(key, self._dataList)

        return allValuesInKey


    def _getListOfAllValuesOfKeyInList(self, key: str, list: list) -> list:
        return [item[key] for item in list]


    def _getItemByValueInKey(self, value, key: str) -> dict:
        item = [item for item in self._dataList if item.get(key) == value]

        if item:
            return item[0]
