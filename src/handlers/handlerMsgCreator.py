import random

import handlers.handlerString
import managers.managerMsgFormats


class HandlerMsgCreator(object):
    def __init__(self, profileTitle: str):
        self.profileTitle = profileTitle
        self.msgDict = dict()
        self.msgTypeTitle = ''

        self.formatManager = managers.managerMsgFormats.ManagerMsgFormats(self.profileTitle)

        self.fieldDescrsList = []
        self.msgTypeContainsMoreThanOneFieldOfUndefinedLength = self.msgTypeContainsMoreThanOneFieldOfUndefinedLength()

        self.listOfFieldValuesInMsg = []

        self.bitMsgLenCount = 0


    def setListOfFieldValuesFromList(self, fieldsValuesList: list) -> None:
        self.listOfFieldValuesInMsg = fieldsValuesList


    def setMsgType(self, msgTypeTitle: str) -> None:
        self.msgTypeTitle = msgTypeTitle


    def getExampleMsgFromMsgTypeDict(self, msgTypeDict: dict) -> str:
        exampleBinMsgString = self.getExampleBinMsgString(msgTypeDict)

        stringHandler = handlers.handlerString.HandlerString()
        exampleMsgString = stringHandler.getHexStrFromBinStr(exampleBinMsgString)

        return exampleMsgString


    def getExampleBinMsgString(self, msgTypeDict: dict) -> str:
        exampleBinMsgString = ''

        fieldDescrsList = msgTypeDict["fieldDescrsList"]
        separator = msgTypeDict["separator"]

        for fieldDescr in fieldDescrsList:
            exampleValueOfField = self.getExampleValueOfField(fieldDescr)

            intBitLen = self.getCurrentFieldBitLength(fieldDescr)

            stringHandler = handlers.handlerString.HandlerString()
            binStrExampleValueOfField = stringHandler.getBinaryStringOfSpecifiedBitLen(exampleValueOfField, intBitLen)

            exampleBinMsgString += binStrExampleValueOfField + ' '

            if fieldDescr["fieldLength"] == 'undef.' and separator != '':
                intSeparator = int(separator, 16)
                exampleBinMsgString += "{0:b}".format(intSeparator)

        return exampleBinMsgString


    def getExampleValueOfField(self, fieldDescr: dict) -> str:
        if self.fieldRangeIsRestricted(fieldDescr):
            listOfValidValues = self.getListOfValidValuesForField(fieldDescr)
            exampleValueOfField = random.choice(listOfValidValues)
        else:
            intBitLen = self.getCurrentFieldBitLength(fieldDescr)
            maxValueForField = self.maxValueForBitLength(intBitLen)
            exampleValueOfField = random.randrange(maxValueForField)

        if fieldDescr["fieldRole"] == 'roleId':
            exampleValueOfField = 0
        elif fieldDescr["fieldRole"] == 'roleLength':
            exampleValueOfField = "x"

        return exampleValueOfField


    def getCurrentFieldBitLength(self, fieldDescrDict: dict) -> int:
        if fieldDescrDict["fieldLength"] == 'undef.':
            length = random.randint(1, 5) * 8
        else:
            length = int(fieldDescrDict["fieldLength"])

        return length


    def maxValueForBitLength(self, bitLength: int) -> int:
        intBitLength = int(bitLength)

        maxValueForBitLength = (2 ** intBitLength) - 1

        return maxValueForBitLength


    def getListOfValidValuesForField(self, fieldDescr: dict) -> list:
        listOfValidValues = []

        for value in fieldDescr["fieldValuesList"]:
            if isinstance(value, str):
                valueToAdd = value.split(' - ')
                intValueToAdd = int(valueToAdd[0], 16)
                listOfValidValues.append(intValueToAdd)
            else:
                listOfValidValues.append(int(value["valueHex"], 16))

        return listOfValidValues


    def getMsgFromListOfPreviouslySetBinFieldsValuesInMsgType(self, msgTypeTitle: str) -> str:
        binMsg = ''
        bitCount = 0

        fieldDescrsList = self.formatManager.getFieldDescrsListForMsgType(msgTypeTitle)

        for fieldIndex, fieldDescr in enumerate(fieldDescrsList):
            if fieldIndex < len(self.listOfFieldValuesInMsg):
                fieldValue = self.listOfFieldValuesInMsg[fieldIndex].strip()
            else:
                fieldValue = ''

            paddedFieldValue, intFieldLength = self.getPaddedFieldValueAndIntFieldLength(fieldValue, fieldDescr)
            binMsg += paddedFieldValue

            if intFieldLength is not None:
                bitCount += intFieldLength

            if bitCount % 8 == 0:
                binMsg += ' '

        stringHandler = handlers.handlerString.HandlerString()
        msg = stringHandler.getHexStrFromBinStr(binMsg)

        return msg


    def getPaddedFieldValueAndIntFieldLength(self, fieldValue: str, fieldDescr: dict) -> tuple:
        fieldLength = fieldDescr["fieldLength"]

        if self.fieldLengthIsUndefined(fieldLength):
            regexpForUndefLengthFieldWithAnyValue = '([0-1]{8})*'
            if fieldValue != regexpForUndefLengthFieldWithAnyValue:
                intFieldLength = len(fieldValue) * 4
            else:
                intFieldLength = None
        else:
            intFieldLength = int(fieldLength)
            fieldLenEntered = len(fieldValue)

            if intFieldLength > fieldLenEntered:
                fieldValue = fieldValue.zfill(intFieldLength)
            elif intFieldLength < fieldLenEntered:
                fieldValue = fieldValue[:intFieldLength]

        return fieldValue, intFieldLength


    def getMsgFromListOfPreviouslySetHexFieldValuesInMsgType(self, msgTypeTitle: str) -> str:
        for indexOfFieldValue, fieldValue in enumerate(self.listOfFieldValuesInMsg):
            strHandler = handlers.handlerString.HandlerString()
            binFieldValue = strHandler.getBinStrFromHexStr(fieldValue)

            fieldLength = self.formatManager.getStrFieldLengthByFieldIndexInMsgType(msgTypeTitle, indexOfFieldValue)

            if not self.fieldLengthIsUndefined(fieldLength):
                if self.fieldValueMarkedAsUndefined(binFieldValue):
                    binFieldValue = 'x' * int(fieldLength)
                else:
                    intFieldLength = int(fieldLength)
                    binFieldValue = binFieldValue.zfill(intFieldLength)
                    binFieldValue = binFieldValue[-intFieldLength:]

            self.listOfFieldValuesInMsg[indexOfFieldValue] = binFieldValue.strip()

        strExampleMsg = self.getMsgFromListOfPreviouslySetBinFieldsValuesInMsgType(msgTypeTitle)

        return strExampleMsg


    def fieldLengthIsUndefined(self, fieldLength: str) -> bool:
        if fieldLength == "undef.":
            return True
        else:
            return False


    def fieldValueMarkedAsUndefined(self, binFieldValue: str) -> bool:
        if binFieldValue != '' and binFieldValue[0] == 'x':
            return True
        else:
            return False


    def getListOfPaddedBinFieldsValues(self, listFieldsValues: list) -> list:
        if len(listFieldsValues) < len(self.fieldDescrsList):
            print('returning 0')
            return listFieldsValues
        self.listOfFieldValuesInMsg = listFieldsValues

        listOfPaddedValues = []

        listFieldsValuesCount = len(self.listOfFieldValuesInMsg)
        for fieldIndex in range(listFieldsValuesCount):
            strBinFieldValue = self.getStrBinFieldValueByFieldIndex(fieldIndex)
            listOfPaddedValues.append(strBinFieldValue)

        return listOfPaddedValues


    def getMsgLenFromListOfFieldValues(self, listFieldsValues: list) -> int:
        msgLen = 0

        fieldValuesCount = len(listFieldsValues)

        for i in range(fieldValuesCount):
            currentFieldLen = self.getFieldLengthByFieldIndex(i)

            index = self.adjustIndexForMsgWithGroupedFieldsInMsgType(i)

            # Separator's length doesn't count in empty undef. length fields, so...
            if self.fieldDescrsList[index].length == 'undef.':
                currentFieldLen += 4 * len(self.msgDict["separator"])

            msgLen += currentFieldLen

        msgLen //= 8

        return msgLen


    def getStrBinFieldValueByFieldIndex(self, fieldIndex: int) -> str:
        strBinFieldValue = self.getStrBinFieldValue(fieldIndex)

        separator = self.getSeparatorIfNeeded(fieldIndex)
        strBinFieldValue += separator

        strBinFieldValue += self.getSpaceIfNeeded(fieldIndex)

        return strBinFieldValue


    def getSpaceIfNeeded(self, fieldIndex: int) -> str:
        fieldLength = self.getFieldLengthByFieldIndex(fieldIndex)
        self.bitMsgLenCount += fieldLength

        if self.bitMsgLenCount % 8 == 0:
            spaceFieldSeparator = ' '
        else:
            spaceFieldSeparator = ''

        return spaceFieldSeparator


    def getStrBinFieldValue(self, fieldIndex: int) -> str:
        if self.fieldLengthIsUndef(fieldIndex):
            strBinFieldValue = self.getStrBinFieldValueForFieldOfUndefLength(fieldIndex)
        else:
            strBinFieldValue = self.getStrBinFieldValueForRegularField(fieldIndex)

        return strBinFieldValue


    def getStrBinFieldValueForFieldOfUndefLength(self, fieldIndex: int) -> str:
        value = self.getFieldValueByIndex(fieldIndex)
        fieldLength = self.getFieldLengthByFieldIndex(fieldIndex)

        strBinFieldValue = '{:0{}b}'.format(int(value), fieldLength // 2)

        if strBinFieldValue == '0':
            strBinFieldValue = ''

        return strBinFieldValue


    def getStrBinFieldValueForRegularField(self, fieldIndex: int) -> str:
        value = self.getFieldValueByIndex(fieldIndex)
        fieldLength = self.getFieldLengthByFieldIndex(fieldIndex)

        stringHandler = handlers.handlerString.HandlerString()

        if self.fieldRoleIsCrc(fieldIndex):
            strBinFieldValue = stringHandler.getBinaryStringOfSpecifiedBitLen("x", fieldLength)
        else:
            strBinFieldValue = stringHandler.getBinaryStringOfSpecifiedBitLen(value, fieldLength)

        return strBinFieldValue


    def getFieldValueByIndex(self, fieldIndex: int) -> str:
        if self.listOfFieldValuesInMsg[fieldIndex] == '':
            value = 0
        else:
            if isinstance(self.listOfFieldValuesInMsg[fieldIndex], str):
                valueInList = self.listOfFieldValuesInMsg[fieldIndex].split(' - ')
                try: value = int(valueInList[0], 16)
                except ValueError:
                    value = 0
            else:
                value = self.listOfFieldValuesInMsg[fieldIndex]

        if self.fieldRoleIsId(fieldIndex):
            strHandler = handlers.handlerString.HandlerString()
            value = strHandler.getHexStrFromBinStr(self.listOfFieldValuesInMsg[fieldIndex])

        fieldIndex = self.adjustIndexForMsgWithGroupedFieldsInMsgType(fieldIndex)

        if fieldIndex < len(self.fieldDescrsList) and self.fieldDescrsList[fieldIndex]["fieldRole"] == 'roleLength':
            value = self.getMsgLenFromListOfFieldValues(self.listOfFieldValuesInMsg)

        return value


    def fieldLengthIsUndef(self, fieldIndex: int) -> bool:
        fieldIndex = self.adjustIndexForMsgWithGroupedFieldsInMsgType(fieldIndex)

        if fieldIndex < len(self.fieldDescrsList) and self.fieldDescrsList[fieldIndex]["fieldLength"] == 'undef.':
            return True
        else:
            return False


    def fieldRoleIsCrc(self, fieldIndex: int) -> bool:
        fieldIndex = self.adjustIndexForMsgWithGroupedFieldsInMsgType(fieldIndex)

        if fieldIndex < len(self.fieldDescrsList) and self.fieldDescrsList[fieldIndex]["fieldRole"] == "roleCrc":
            return True
        else:
            return False


    def fieldRoleIsId(self, fieldIndex: int) -> bool:
        fieldIndex = self.adjustIndexForMsgWithGroupedFieldsInMsgType(fieldIndex)

        if fieldIndex < len(self.fieldDescrsList) and self.fieldDescrsList[fieldIndex]["fieldRole"] == "roleId":
            return True
        else:
            return False


    def adjustIndexForMsgWithGroupedFieldsInMsgType(self, fieldIndex: int) -> int:
        indexOfFirstFieldInGroup = self.formatManager.getIndexOfFirstFieldInGroupInMsgType(self.msgTypeTitle)
        indexOfLastFieldInGroup = self.formatManager.getIndexOfLastFieldInGroupInMsgType(self.msgTypeTitle)

        self.indexOfLastFieldTitleInGroup = self.formatManager.getIndexOfLastFieldInGroupInMsgType(self.msgTypeTitle)

        lengthOfGroupedFields = self.formatManager.getLengthOfGroupedFieldsInMsgType(self.msgTypeTitle)

        if indexOfFirstFieldInGroup is not None and indexOfLastFieldInGroup is not None and self.indexOfTale(fieldIndex):
            while fieldIndex > len(self.fieldDescrsList) - 1 and indexOfLastFieldInGroup > 0:
                fieldIndex -= lengthOfGroupedFields
        else:
            while indexOfLastFieldInGroup in range(fieldIndex):
                fieldIndex -= lengthOfGroupedFields

        return fieldIndex


    def indexOfTale(self, fieldIndex: int) -> bool:
        taleLen = self.formatManager.getCountOfTaleFieldsInMsgType()
        taleStartIndex = len(self.listOfFieldValuesInMsg) - taleLen

        if fieldIndex in range(taleStartIndex, taleStartIndex + taleLen):
            return True
        else:
            return False


    def getBinRegexpOfGroupedField(self) -> str:
        binRegexpOfGroupedField = ''

        formingGroupedFields = False

        firstFieldTitleInGroup = self.msgDict["firstFieldTitleInGroup"]
        lastFieldTitleInGroup = self.msgDict["lastFieldTitleInGroup"]

        for descr in self.fieldDescrsList:
            if descr["fieldTitle"] == firstFieldTitleInGroup or formingGroupedFields:
                formingGroupedFields = True
                if descr["fieldLength"] == 'undef.':
                    binRegexpOfGroupedField += '([0-1]{8})*'
                else:
                    binRegexpOfGroupedField += '[0-1]{' + descr["fieldLength"] +'}'

            if descr["fieldTitle"] == lastFieldTitleInGroup:
                formingGroupedFields = False
                break

        return binRegexpOfGroupedField


    def getIndexOfStartFieldInGroup(self) -> int:
        firstFieldTitleInGroup = self.msgDict["firstFieldTitleInGroup"]

        indexOffirstFieldTitleInGroup = -1

        for fieldIndex, descr in enumerate(self.fieldDescrsList):
            if descr["fieldTitle"] == firstFieldTitleInGroup:
                indexOffirstFieldTitleInGroup = fieldIndex
                break

        return indexOffirstFieldTitleInGroup


    def getIndexOfEndFieldInGroup(self) -> int:
        lastFieldTitleInGroup = self.msgDict["lastFieldTitleInGroup"]

        indexOflastFieldTitleInGroup = -1

        for fieldIndex, descr in enumerate(self.fieldDescrsList):
            if descr["fieldTitle"] == lastFieldTitleInGroup:
                indexOflastFieldTitleInGroup = fieldIndex
                break

        return indexOflastFieldTitleInGroup


    def processingFirstFieldInGroup(self, descrIndex: int):
        firstFieldTitleInGroup = self.msgDict["firstFieldTitleInGroup"]

        if self.fieldDescrsList[descrIndex]["fieldTitle"] == firstFieldTitleInGroup:
            return True
        else:
            return False


    def getSeparatorIfNeeded(self, fieldIndex: int) -> str:
        fieldIndex = self.adjustIndexForMsgWithGroupedFieldsInMsgType(fieldIndex)
        fieldDescr = self.fieldDescrsList[fieldIndex]
        fieldLength = fieldDescr["fieldLength"]

        msgDescrsCount = len(self.fieldDescrsList)

        separator = self.msgDict["separator"]

        binStrSeparator = ''

        if fieldIndex in range(1, msgDescrsCount):
            if self.msgTypeContainsMoreThanOneFieldOfUndefinedLength and self.fieldLengthIsUndefined(fieldLength):
                intSeparator = int(separator, 16)
                binStrSeparator = "{0:b}".format(intSeparator)

        return binStrSeparator


    def msgTypeContainsMoreThanOneFieldOfUndefinedLength(self) -> bool:
        undefLengthFieldsCount = 0

        for fieldDescr in self.fieldDescrsList:
            fieldLength = fieldDescr["fieldLength"]

            if self.fieldLengthIsUndefined(fieldLength):
                undefLengthFieldsCount += 1

            if undefLengthFieldsCount > 1:
                return True

        return False


    def getFieldLengthByFieldIndex(self, fieldIndex: int) -> int:
        fieldIndex = self.adjustIndexForMsgWithGroupedFieldsInMsgType(fieldIndex)

        if fieldIndex >= len(self.fieldDescrsList):
            return 0

        if self.fieldDescrsList[fieldIndex]["fieldLength"] == 'undef.':
            fieldLength = 4 * len(str(self.listOfHexFieldValuesInMsg[fieldIndex]))
        else:
            fieldLength = self.getCurrentFieldBitLength(self.fieldDescrsList[fieldIndex])

        return fieldLength


    def someFieldsAreShorterThenByte(self) -> bool:
        result = False

        for fieldDescr in self.fieldDescrsList:
            if fieldDescr["fieldLength"] == 'undef.':
                continue
            elif int(fieldDescr["fieldLength"]) < 8:
                result = True

        return result


    def fieldRangeIsRestricted(self, fieldDescrDict: dict) -> bool:
        result = False

        if len(fieldDescrDict["fieldValuesList"]) > 0:
            result = True

        return result
