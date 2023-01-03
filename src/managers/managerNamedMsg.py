import json


class ManagerNamedMsg(object):
    """
    Class for saving and retrieving user-created named messages
    """
    def __init__(self, profileTitle: str):
        self.profileTitle = profileTitle
        self.namedMsgListFilePath = './__profiles__/' + profileTitle + '/namedMsgList.json'

        self.namedMsgList = self.readNamedMsgsFromFile()


    def readNamedMsgsFromFile(self) -> list:
        namedMsgList = list()

        try:
            with open(self.namedMsgListFilePath, 'r', newline='') as namedMsgListFile:
                namedMsgList = json.load(namedMsgListFile)
        except IOError:
            with open(self.namedMsgListFilePath, 'a') as namedMsgListFile:
                json.dump(namedMsgList, namedMsgListFile, indent=4, ensure_ascii=False)
        except json.decoder.JSONDecodeError:
            with open(self.namedMsgListFilePath, 'a') as namedMsgListFile:
                json.dump(namedMsgList, namedMsgListFile, indent=4, ensure_ascii=False)

        self.namedMsgList = namedMsgList

        return namedMsgList


    def switchToProfile(self, profileTitle: str) -> None:
        self.namedMsgListFilePath = './__profiles__/' + profileTitle + '/namedMsgList.json'


    def addNewNamedMsg(self, namedMsgDict: dict) -> None:
        self.namedMsgList.append(namedMsgDict)
        self.updateNamedMsgListFile(self.namedMsgList)


    def removeNamedMsg(self, msgTypeTitleToDel: str) -> None:
        for namedMsg in self.namedMsgList:
            if namedMsg["msgTitle"] == msgTypeTitleToDel:
                self.namedMsgList.remove(namedMsg)


    def updateNamedMsgListFile(self, newNamedMsgList: list) -> None:
        with open(self.namedMsgListFilePath, 'w', newline='') as namedMsgListFile:
            json.dump(newNamedMsgList, namedMsgListFile, indent=4, ensure_ascii=False)


    def getAllNamedMsgList(self) -> list:
        return self.namedMsgList


    def getAllNamedMsgTitlesList(self) -> list:
        print("self.namedMsgList in manager", self.namedMsgList)
        return [namedMsg["msgTitle"] for namedMsg in self.namedMsgList]


    def getHexStrByMsgTitle(self, msgName: str) -> str:
        for namedMsg in self.namedMsgList:
            if namedMsg["msgTitle"] == msgName:
                return namedMsg["msgHex"]
        return ""


    def getNamedMsgTitleFromHexStr(self, msgHex: str) -> str:
        for namedMsg in self.namedMsgList:
            if namedMsg["msgHex"] == msgHex:
                return namedMsg["msgTitle"]
        return ""
