import os

import src.managers.ioManager as ioManager


class ManagerNamedRegexp(ioManager.IoManager):
    """
    Class for saving and retrieving regular expressions for messages
    """
    def __init__(self, profileTitle: str):
        super().__init__(profileTitle)
        self._dataListFilePath = './__profiles__/' + profileTitle + '/namedRegexpList.json'
        self._dataList = super().readDataFromFile()

        if not os.path.exists(self._dataListFilePath):
            super()._createEmptyFile(self._dataListFilePath)


    def removeRegexpByTitle(self, regexpTitleToRemove: str) -> None:
        self._removeItemFromDataListByValueInKey(regexpTitleToRemove, "regexpTitle")


    def getAllNamedRegexpTitlesList(self) -> list:
        allNamedRegexpTitlesList = self._getListOfAllValuesInKey("regexpTitle")
        return allNamedRegexpTitlesList


    def getBinRegexpFromRegexpTitle(self, regexpTitle: str) -> str:
        namedRegexp = self._getItemByValueInKey(regexpTitle, "regexpTitle")
        if namedRegexp is None:
            return ""
        else:
            return namedRegexp["regexpBinStr"]


    def getBinRegexpsListFromRegexpTitlesList(self, regexpTitlesList: list) -> list:
        binRegexpsList = []

        for regexpTitle in regexpTitlesList:
            binRegexp = self.getBinRegexpFromRegexpTitle(regexpTitle)

            if binRegexp != "":
                binRegexpsList.append(binRegexp)

        return binRegexpsList


    def getNamedMsgNameFromHexStr(self, regexpBinStr: str) -> str:
        namedRegexp = self._getItemByValueInKey(regexpBinStr, "regexpBinStr")
        if namedRegexp is None:
            return ""
        else:
            return namedRegexp["regexpTitle"]
