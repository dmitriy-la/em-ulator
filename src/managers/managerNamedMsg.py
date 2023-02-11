import src.managers.ioManager as ioManager


class ManagerNamedMsg(ioManager.IoManager):
    """
    Class for saving and retrieving user-created named messages
    """
    def __init__(self, profileTitle: str):
        super().__init__(profileTitle)
        self._dataListFilePath = './__profiles__/' + profileTitle + '/namedMsgList.json'
        self._dataList = self.readDataFromFile()


    def removeNamedMsg(self, msgTypeTitleToRemove: str) -> None:
        self._removeItemFromDataListByValueInKey(msgTypeTitleToRemove, "msgTitle")


    def getAllNamedMsgTitlesList(self) -> list:
        allNamedMsgTitlesList = self._getListOfAllValuesInKey("msgTitle")
        return allNamedMsgTitlesList


    def getHexStrByMsgTitle(self, msgTitle: str) -> str:
        namedMsg = self._getItemByValueInKey(msgTitle, "msgTitle")
        if namedMsg is None:
            return ""
        else:
            return namedMsg["msgHex"]


    def getNamedMsgTitleFromHexStr(self, msgHex: str) -> str:
        namedMsg = self._getItemByValueInKey(msgHex, "msgHex")
        if namedMsg is None:
            return ""
        else:
            return namedMsg["msgTitle"]
