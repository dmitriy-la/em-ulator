import json


class ManagerNamedRegexp(object):
    """
    Class for saving and retrieving regular expressions for messages
    """
    def __init__(self, profileTitle: str):
        self.profileTitle = profileTitle
        self.namedRegexpListFilePath = './__profiles__/' + profileTitle + '/namedRegexpList.json'

        self.namedRegexpList = self.readNamedRegexpsFromFile()


    def readNamedRegexpsFromFile(self) -> list:
        namedRegexpList = list()

        try:
            with open(self.namedRegexpListFilePath, 'r', newline='') as namedRegexpListFile:
                namedRegexpList = json.load(namedRegexpListFile)
        except IOError:
            print("IOError")
            with open(self.namedRegexpListFilePath, 'a') as namedRegexpListFile:
                json.dump(namedRegexpList, namedRegexpListFile, indent=4, ensure_ascii=False)
        except json.decoder.JSONDecodeError:
            print("JSONDecodeError")
            with open(self.namedRegexpListFilePath, 'a') as namedRegexpListFile:
                json.dump(namedRegexpList, namedRegexpListFile, indent=4, ensure_ascii=False)

        self.namedRegexpList = namedRegexpList

        return namedRegexpList


    def switchToProfile(self, profileTitle: str) -> None:
        self.namedRegexpListFilePath = './__profiles__/' + profileTitle + '/namedRegexpList.json'


    def addNewNamedRegexp(self, namedMsgDict: dict) -> None:
        self.namedRegexpList.append(namedMsgDict)
        self.updateNamedRegexpListFile(self.namedRegexpList)


    def removeRegexpByTitle(self, regexpTitleToRemove: str) -> None:
        for namedRegexp in self.namedRegexpList:
            if namedRegexp["regexpTitle"] == regexpTitleToRemove:
                self.namedRegexpList.remove(namedRegexp)


    def updateNamedRegexpListFile(self, newNamedRegexpList: list) -> None:
        with open(self.namedRegexpListFilePath, 'w', newline='') as namedRegexpListFile:
            json.dump(newNamedRegexpList, namedRegexpListFile, indent=4, ensure_ascii=False)


    def getAllNamedRegexpList(self) -> list:
        return self.namedRegexpList


    def getAllNamedRegexpTitlesList(self) -> list:
        return [regexpDescr["regexpTitle"] for regexpDescr in self.namedRegexpList]


    def getBinRegexpFromRegexpTitle(self, regexpTitle: str) -> str:
        for namedRegexp in self.namedRegexpList:
            if namedRegexp["regexpTitle"] == regexpTitle:
                return namedRegexp["regexpBinStr"]
        return ""


    def getBinRegexpsListFromRegexpTitlesList(self, regexpTitlesList: list) -> list:
        binRegexpsList = []

        for regexpTitle in regexpTitlesList:
            binRegexp = self.getBinRegexpFromRegexpTitle(regexpTitle)

            if binRegexp != "":
                binRegexpsList.append(binRegexp)

        return binRegexpsList


    def getNamedMsgNameFromHexStr(self, msgHex: str) -> str:
        for namedMsg in self.namedRegexpList:
            if namedMsg["regexpBinStr"] == msgHex:
                return namedMsg["regexpTitle"]
        return ""
