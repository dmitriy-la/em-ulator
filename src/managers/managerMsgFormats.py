import src.managers.ioManager as ioManager


class ManagerMsgFormats(ioManager.IoManager):
    def __init__(self, profileTitle='default'):
        super().__init__(profileTitle)

        self._dataListFilePath = self.getMsgFormatsFilePath()
        self._dataList = self.readDataFromFile()


    def getMsgFormatsFilePath(self) -> str:
        return './__profiles__/' + self.profileTitle + '/msgFormats.json'


    def setCurrentProfile(self, newProfileTitle: str) -> None:
        self.profileTitle = newProfileTitle


    def addNewMsgType(self, newMsgTypeDict: dict) -> None:
        self.addItemToDataList(newMsgTypeDict)


    def removeMsgType(self, msgTypeTitle: str) -> None:
        self._removeItemFromDataListByValueInKey(msgTypeTitle, 'msgTypeTitle')


    def updateMsgType(self, msgTypeDict: dict) -> None:
        self._replaceItemInDataListByKey(msgTypeDict, "msgTypeTitle")


    def updateAllFormatsFromAllMsgTypesList(self, allMsgTypesList: list) -> None:
        self._dataList = allMsgTypesList
        self.updateDataFile(self._dataList)


    def getListOfAllMsgTypeDescrs(self) -> list:
        return self._dataList


    def getInfoForMsgType(self, msgTypeTitle: str) -> dict:
        msgTypeDict = self._getItemByValueInKey(msgTypeTitle, "msgTypeTitle")

        if not msgTypeDict:
            msgTypeDict = {"msgTypeTitle": "undef"}

        return msgTypeDict


    def getIfMsgTypeIsReceipt(self, msgTypeTitle: str) -> bool:
        msgTypeDict = self.getInfoForMsgType(msgTypeTitle)

        if msgTypeDict['msgTypeTitle'] == "undef":
            return False
        elif msgTypeDict['isReceipt']:
            return True
        else:
            return False


    def getFieldDescrsListForMsgType(self, msgTypeTitle: str) -> list:
        msgTypeDict = self._getItemByValueInKey(msgTypeTitle, 'msgTypeTitle')

        if not msgTypeDict:
            return []
        else:
            return msgTypeDict["fieldDescrsList"]


    def getFieldInfoByFieldTitleInMsgType(self, fieldTitle: str, msgTypeTitle: str) -> dict:
        msgDescrsList = self.getFieldDescrsListForMsgType(msgTypeTitle)

        for fieldDescr in msgDescrsList:
            if fieldDescr['fieldTitle'] == fieldTitle:
                return fieldDescr

        return {"fieldTitle": "undef"}


    def getLengthOfFieldExcludedFromLenCountInMsgType(self, msgTypeTitle: str) -> int:
        msgTypeDict = self.getInfoForMsgType(msgTypeTitle)
        msgTypeTitle = msgTypeDict["msgTypeTitle"]

        if msgTypeTitle == "undef":
            lengthOfFieldExcludedFromLenCount = 0
        else:
            titleOfFieldExcludedFromLenCount = self.getTitleOfFieldExcludedFromLenCountInMsgType(msgTypeTitle)

            args = [msgTypeTitle, titleOfFieldExcludedFromLenCount]
            lengthOfFieldExcludedFromLenCount = self.getFieldLengthByFieldTitleInMsgType(*args)

        return lengthOfFieldExcludedFromLenCount


    def getTitleOfFieldExcludedFromLenCountInMsgType(self, msgTypeTitle: str) -> str:
        msgTypeDict = self.getInfoForMsgType(msgTypeTitle)
        titleOfFieldExcludedFromLenCount = msgTypeDict["fieldExcludedFromLenCount"]

        return titleOfFieldExcludedFromLenCount


    def getFieldLengthByFieldTitleInMsgType(self, msgTypeTitle: str, fieldTitle: str) -> int:
        fieldDescrsList = self.getFieldDescrsListForMsgType(msgTypeTitle)

        fieldLength = 0

        for fieldDescr in fieldDescrsList:
            if fieldDescr['fieldTitle'] == fieldTitle:
                strFieldLength = fieldDescr['fieldLength']
                fieldLength = int(strFieldLength)
                return fieldLength

        return fieldLength


    def getStrFieldLengthByFieldIndexInMsgType(self, msgTypeTitle: str, fieldIndex: int) -> str:
        fieldDescrsList = self.getFieldDescrsListForMsgType(msgTypeTitle)

        fieldDescr = fieldDescrsList[fieldIndex]
        strFieldLength = fieldDescr['fieldLength']

        return strFieldLength


    def getInfoForReceiptMsg(self) -> dict:
        msgTypeDict = self._getItemByValueInKey(True, 'isReceipt')

        return msgTypeDict


    def getSeparatorForMsgType(self, msgTypeTitle: str) -> str:
        msgTypeDict = self._getItemByValueInKey(msgTypeTitle, 'msgTypeTitle')

        return msgTypeDict['separator']


    def getBinSeparatorForMsgType(self, msgTypeTitle: str) -> str:
        separator = self.getSeparatorForMsgType(msgTypeTitle)

        if separator != '':
            binSeparator = '{0:b}'.format(int(separator, 16))
        else:
            binSeparator = ''

        return binSeparator


    def getListOfAllMsgTypeTitles(self) -> list:
        allMsgTypeTitles = self._getListOfAllValuesInKey("msgTypeTitle")
        return allMsgTypeTitles


    def getListOfTypesValues(self) -> list:
        listOfTypesValues = []

        for msgTypeDict in self._dataList:
            msgTypeTitle = msgTypeDict["msgTypeTitle"]
            indexOfFieldWithType = self.getIndexOfFieldWithRoleTypeInMsgType(msgTypeTitle)
            fieldDescrOfFieldWithType = msgTypeDict["fieldDescrsList"][indexOfFieldWithType]

            descrOfValueOfFieldWithType = fieldDescrOfFieldWithType["fieldValuesList"][0]
            msgTypeValueHex = descrOfValueOfFieldWithType["valueHex"]

            listOfTypesValues.extend(msgTypeValueHex)

        return listOfTypesValues


    def getIndexOfFieldWithRoleIdInMsgType(self, msgTypeTitle: str) -> int:
        fieldRole = "roleId"

        fieldIndex = self._getIndexOfFieldWithSpecificRoleInMsgType(msgTypeTitle, fieldRole)

        return fieldIndex


    def getIndexOfFieldWithRoleLengthInMsgType(self, msgTypeTitle: str) -> int:
        fieldRole = "roleLength"

        fieldIndex = self._getIndexOfFieldWithSpecificRoleInMsgType(msgTypeTitle, fieldRole)

        return fieldIndex


    def getIndexOfFieldWithRoleTypeInMsgType(self, msgTypeTitle: str) -> int:
        fieldRole = "roleType"

        fieldIndex = self._getIndexOfFieldWithSpecificRoleInMsgType(msgTypeTitle, fieldRole)

        return fieldIndex


    def getIndexOfFieldWithRoleCrcInMsgType(self, msgTypeTitle: str) -> int:
        fieldRole = "roleCrc"

        fieldIndex = self._getIndexOfFieldWithSpecificRoleInMsgType(msgTypeTitle, fieldRole)

        return fieldIndex


    def _getIndexOfFieldWithSpecificRoleInMsgType(self, msgTypeTitle: str, fieldRole: str) -> int:
        msgDict = self.getInfoForMsgType(msgTypeTitle)

        fieldDescrsList = msgDict["fieldDescrsList"]

        fieldDescr = self._getFieldDescrByFieldRoleInFieldDescrsList(fieldRole, fieldDescrsList)
        fieldIndex = fieldDescrsList.index(fieldDescr)

        return fieldIndex


    def _getFieldDescrByFieldRoleInFieldDescrsList(self, fieldRole: str, fieldDescrsList: list):
        for fieldIndex, fieldDescr in enumerate(fieldDescrsList):
            if fieldDescr["fieldRole"] == fieldRole:
                return fieldDescr


    def getLengthOfFieldWithRoleCrcInMsgType(self, msgTypeTitle: str) -> int:
        fieldRole = "roleCrc"

        fieldLength = self.getLengthOfFieldWithSpecificRoleInMsgType(msgTypeTitle, fieldRole)

        return fieldLength


    def getLengthOfFieldWithRoleLengthInMsgType(self, msgTypeTitle: str) -> int:
        fieldRole = "roleLength"

        fieldLength = self.getLengthOfFieldWithSpecificRoleInMsgType(msgTypeTitle, fieldRole)

        return fieldLength


    def getLengthOfFieldWithRoleIdInMsgType(self, msgTypeTitle: str) -> int:
        fieldRole = "roleId"

        fieldLength = self.getLengthOfFieldWithSpecificRoleInMsgType(msgTypeTitle, fieldRole)

        return fieldLength


    def getLengthOfFieldWithSpecificRoleInMsgType(self, msgTypeTitle: str, fieldRole: str) -> int:
        fieldDescrsList = self.getFieldDescrsListForMsgType(msgTypeTitle)

        fieldDescr = self._getFieldDescrByFieldRoleInFieldDescrsList(fieldRole, fieldDescrsList)

        if fieldDescr is None:
            intFieldLength = 0
        else:
            intFieldLength = int(fieldDescr["fieldLength"])

        return intFieldLength


    def getFieldIndexByTitleInMsgType(self, msgTypeTitle: str, fieldTitle: str) -> int:
        msgDict = self.getInfoForMsgType(msgTypeTitle)

        fieldDescrsList = msgDict["fieldDescrsList"]

        for fieldIndex, fieldDescr in enumerate(fieldDescrsList):
            if fieldDescr["fieldTitle"] == fieldTitle:
                return fieldIndex


    def getMsgLengthByMsgType(self, msgTypeTitle: str) -> int:
        msgDict = self.getInfoForMsgType(msgTypeTitle)

        if msgDict["msgTypeTitle"] == "undef":
            return 0

        fieldDescrsList = msgDict["fieldDescrsList"]

        msgFieldsLengthList = self._getListOfAllValuesOfKeyInList("fieldLength", fieldDescrsList)
        msgFieldsLengthList = list(filter(lambda fieldLen: fieldLen != "undef.", msgFieldsLengthList))

        return sum(msgFieldsLengthList)


    def fieldIsFirstFieldInGroupInMsgType(self, fieldTitle: str, msgTypeTitle: str) -> bool:
        msgTypeInfo = self.getInfoForMsgType(msgTypeTitle)

        if fieldTitle == msgTypeInfo["firstFieldTitleInGroup"]:
            return True
        else:
            return False


    def getIndexOfFirstFieldInGroupInMsgType(self, msgTypeTitle: str) -> int:
        """
        :return:
        """
        firstGroupedFieldTitleInGroup = self.getTitleOfFirstFieldInGroupInMsgType(msgTypeTitle)

        indexOfFirstFieldInGroup = self.getFieldIndexByTitleInMsgType(msgTypeTitle, firstGroupedFieldTitleInGroup)

        return indexOfFirstFieldInGroup


    def getTitleOfFirstFieldInGroupInMsgType(self, msgTypeTitle: str) -> str:
        msgTypeInfo = self.getInfoForMsgType(msgTypeTitle)
        titleOfFirstFieldInGroup = msgTypeInfo["firstFieldTitleInGroup"]

        return titleOfFirstFieldInGroup


    def fieldIsLastFieldInGroupInMsgType(self, fieldTitle: str, msgTypeTitle: str) -> bool:
        msgTypeInfo = self.getInfoForMsgType(msgTypeTitle)

        if fieldTitle == msgTypeInfo["lastFieldTitleInGroup"]:
            return True
        else:
            return False


    def getIndexOfLastFieldInGroupInMsgType(self, msgTypeTitle: str) -> int:
        """
        :return:
        """
        titleOfLastFieldInGroup = self.getTitleOfLastFieldInGroupInMsgType(msgTypeTitle)

        indexOfLastFieldInGroup = self.getFieldIndexByTitleInMsgType(msgTypeTitle, titleOfLastFieldInGroup)

        return indexOfLastFieldInGroup


    def getTitleOfLastFieldInGroupInMsgType(self, msgTypeTitle: str) -> str:
        msgTypeInfo = self.getInfoForMsgType(msgTypeTitle)
        titleOfLastFieldInGroup = msgTypeInfo["lastFieldTitleInGroup"]

        return titleOfLastFieldInGroup


    def getLengthOfGroupedFieldsInMsgType(self, msgTypeTitle: str) -> int:
        indexOfLastFieldInGroup = self.getIndexOfLastFieldInGroupInMsgType(msgTypeTitle)
        indexOfFirstFieldInGroup = self.getIndexOfFirstFieldInGroupInMsgType(msgTypeTitle)

        if indexOfFirstFieldInGroup is None or indexOfLastFieldInGroup is None:
            lengthOfGroupedFields = 0
        else:
            lengthOfGroupedFields = indexOfLastFieldInGroup - indexOfFirstFieldInGroup

        return lengthOfGroupedFields


    def getCountOfTaleFieldsInMsgType(self, msgTypeTitle: str) -> int:
        """
        Gets count of "tale" fields in message with groups.
        "Tale" refers to fields that are not included in groups and follow after last group.
        :return:
        """
        indexOfLastFieldInGroup = self.getIndexOfLastFieldInGroupInMsgType(msgTypeTitle)
        fieldsCount = self.getFieldsCountInMsgType(msgTypeTitle)
        indexOfLastFieldInMsgType = fieldsCount - 1

        lenOfTaleFields = indexOfLastFieldInMsgType - indexOfLastFieldInGroup

        return lenOfTaleFields


    def getFieldsCountInMsgType(self, msgTypeTitle: str) -> int:
        fieldDescrsList = self.getFieldDescrsListForMsgType(msgTypeTitle)
        fieldsCount = len(fieldDescrsList)

        return fieldsCount


    def thereIsMoreThanOneFieldOfUndefLengthInMsgType(self, msgTypeTitle: str) -> bool:
        fieldLengthsList = self.getListOfAllFieldsLengthInMsgType(msgTypeTitle)

        if fieldLengthsList.count('undef.') > 1:
            return True
        else:
            return False


    def getBinLenOfFieldsAfterSingleUndefFieldInMsgType(self, msgTypeTitle: str) -> int:
        listOfAllFieldsLength = self.getListOfAllFieldsLengthInMsgType(msgTypeTitle)
        indexOfFirstFieldOfUndefLength = self.getIndexOfFirstFieldOfUndefLengthInMsgType(msgTypeTitle)

        totalBinLenOfFieldsAfterUndefField = sum(listOfAllFieldsLength[indexOfFirstFieldOfUndefLength + 1:])

        return totalBinLenOfFieldsAfterUndefField


    def getIndexOfFirstFieldOfUndefLengthInMsgType(self, msgTypeTitle: str) -> int:
        fieldLengthsList = self.getListOfAllFieldsLengthInMsgType(msgTypeTitle)

        try:
            indexOfFirstFieldOfUndefLength = fieldLengthsList.index('undef.')
        except ValueError:
            indexOfFirstFieldOfUndefLength = None

        return indexOfFirstFieldOfUndefLength


    def getListOfAllFieldsLengthInMsgType(self, msgTypeTitle: str) -> list:
        fieldDescrsList = self.getFieldDescrsListForMsgType(msgTypeTitle)

        fieldLengthsList = self._getListOfAllValuesOfKeyInList("fieldLength", fieldDescrsList)

        return fieldLengthsList


    @staticmethod
    def fieldLenIsUndef(fieldDescr: dict) -> bool:
        if fieldDescr["fieldLength"] == 'undef.':
            return True
        else:
            return False


    @staticmethod
    def fieldValuesAreRestricted(fieldDescr: dict) -> bool:
        if len(fieldDescr["fieldValuesList"]) > 0 and fieldDescr["fieldLength"] != 'undef.':
            return True
        else:
            return False


    @staticmethod
    def fieldRoleIsLength(fieldDescr: dict) -> bool:
        if fieldDescr["fieldRole"] == 'roleLength':
            return True
        else:
            return False


    @staticmethod
    def fieldRoleIsId(fieldDescr: dict) -> bool:
        if fieldDescr["fieldRole"] == 'roleId':
            return True
        else:
            return False


    @staticmethod
    def fieldRoleIsCrc(fieldDescr: dict) -> bool:
        if fieldDescr["fieldRole"] == 'roleCrc':
            return True
        else:
            return False


    @staticmethod
    def fieldRoleIsType(fieldDescr: dict) -> bool:
        if fieldDescr["fieldRole"] == 'roleType':
            return True
        else:
            return False
