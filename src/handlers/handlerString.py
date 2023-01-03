class HandlerString(object):
    """
    Class for performing general string processing
    """
    def __init__(self):
        self.listOfAllSpacesIndexes = []
        self.bitCount = 0
        self.savedBitsForBitFields = ""
        self.savedBitsLen = 0


    def getWholeMsgBinStrFromHexStr(self, hexStr: str) -> str:
        if isinstance(hexStr, bytes):
            hexStr = hexStr.decode('utf-8', 'replace')

        hexStr = hexStr.strip()
        listOfHexFields = hexStr.split(' ')
        binStr = ''

        for hexFieldStr in listOfHexFields:
            binFieldStr = self.getBinFieldStr(hexFieldStr)
            binStr += binFieldStr + ' '

        binStr = binStr[:-1]

        return binStr


    def getBinFieldStr(self, hexFieldStr: str) -> str:
        if hexFieldStr == '([0-1]{8})*':
            binFieldStr = '([0-1]{8})*'
        else:
            try:
                intHexFieldStr = int(hexFieldStr, 16)
                lenOfHexFieldStr = len(hexFieldStr) * 4
                binFieldStr = '{:0{}b}'.format(intHexFieldStr, lenOfHexFieldStr)
            except ValueError:
                lenOfHexFieldStr = len(hexFieldStr) * 4
                binFieldStr = 'x' * lenOfHexFieldStr

        return binFieldStr


    def getBinaryStringOfSpecifiedBitLen(self, valueToConvert: str, bitLength: int) -> str:
        if self.fieldValueToPadIsUndef(valueToConvert):
            paddedBinStr = 'x' * int(bitLength)
        else:
            binStr = "{0:b}".format(int(valueToConvert))
            paddedBinStr = binStr.zfill(int(bitLength))

        return paddedBinStr


    def fieldValueToPadIsUndef(self, valueToConvert) -> bool:
        if isinstance(valueToConvert, str) and valueToConvert == 'x':
            return True
        else:
            return False


    def getHexStrFromBinList(self, binList: list) -> str:
        strBinMsg = ''

        for binField in binList:
            strBinMsg += binField
            strBinMsg += ' '

        strBinMsg = strBinMsg.strip(" ")

        hexMsg = self.getHexStrFromBinStr(strBinMsg)

        return hexMsg


    def getHexStrFromBinStr(self, binStr: str) -> str:
        listOfBinFields = binStr.split(' ')
        hexStr = ''

        self.bitCount = 0
        self.savedBitsForBitFields = ""
        self.savedBitsLen = 0

        for binFieldStr in listOfBinFields:
            hexFieldStr = self.getHexFieldStrFromBinFieldStr(binFieldStr)
            hexStr += hexFieldStr + ' '

        return hexStr


    def getHexFieldStrFromBinFieldStr(self, binFieldStr: str) -> str:
        if binFieldStr == '([0-1]{8})*':
            hexFieldStr = self.getHexFieldStrForFieldOfUndefLen()
        elif binFieldStr != '' and 'x' in binFieldStr:
            hexFieldStr = self.getHexFieldStrForAnyValueBinField(binFieldStr)
        elif binFieldStr != '':
            hexFieldStr = self.getHexFieldStrForRegularField(binFieldStr)
        else:
            hexFieldStr = ''

        return hexFieldStr


    def getHexFieldStrForRegularField(self, binFieldStr: str) -> str:
        hexFieldStr = ''

        bitFieldLen = len(binFieldStr)
        self.bitCount += bitFieldLen
        if self.bitCount % 8 == 0:
            if self.savedBitsForBitFields != "":
                self.savedBitsForBitFields += binFieldStr
                self.savedBitsLen += len(binFieldStr)

                hexFieldStr = '{:0{}X}'.format(int(self.savedBitsForBitFields, 2), self.savedBitsLen // 4)
                self.savedBitsForBitFields = ""
            else:
                hexFieldStr = '{:0{}X}'.format(int(binFieldStr, 2), len(binFieldStr) // 4)
        else:
            self.savedBitsLen += len(binFieldStr)
            self.savedBitsForBitFields += binFieldStr

        return hexFieldStr


    def getHexFieldStrForFieldOfUndefLen(self) -> str:
        bitFieldLen = 8
        self.bitCount += bitFieldLen
        hexFieldStr = '([0-1]{8})*'

        return hexFieldStr


    def getHexFieldStrForAnyValueBinField(self, binFieldStr: str) -> str:
        bitFieldLen = len(binFieldStr)
        self.bitCount += bitFieldLen

        hexFieldLen = bitFieldLen // 4
        hexFieldStr = 'x' * hexFieldLen

        return hexFieldStr


    def getBinStrFromHexStr(self, hexStr: str) -> str:
        hexStr = hexStr.replace(' - ', ' ')
        listOfHexFields = hexStr.split(' ')

        listOfBinFields = []
        for hexFieldStr in listOfHexFields:
            binFieldStr = self.getBinFieldStrFromHexFieldStr(hexFieldStr)
            listOfBinFields.append(binFieldStr)

        binStr = ' '.join(listOfBinFields)

        return binStr


    def getBinFieldStrFromHexFieldStr(self, hexFieldStr: str) -> str:
        if hexFieldStr == '([0-1]{8})*':
            binFieldStr = '([0-1]{8})*'
        elif hexFieldStr != '' and 'x' in hexFieldStr:
            fieldLen = len(hexFieldStr) * 4
            binFieldStr = 'x' * fieldLen
        elif hexFieldStr != '':
            fieldValue = int(hexFieldStr, 16)
            fieldLen = len(hexFieldStr) * 4
            binFieldStr = '{:0{}b}'.format(fieldValue, fieldLen)
        else:
            binFieldStr = ''

        return binFieldStr


    def saveIndexesOfSpacesInHexMsg(self, msgWithoutId: str) -> list:
        self.listOfAllSpacesIndexes = [pos for pos, char in enumerate(msgWithoutId.strip(' ')) if char == ' ']
        return self.listOfAllSpacesIndexes


    def restoreSpacesInHexMsg(self, msg: str) -> str:
        listOfStingToConcatIntoMsgWithSpaces = []
        beginIndex = 0
        for spaceIndex in self.listOfAllSpacesIndexes:
            adjustedSpaceIndex = (spaceIndex - self.listOfAllSpacesIndexes.index(spaceIndex))
            listOfStingToConcatIntoMsgWithSpaces.append(msg[beginIndex: adjustedSpaceIndex])
            beginIndex = adjustedSpaceIndex

        # Adding last field
        listOfStingToConcatIntoMsgWithSpaces.append(msg[beginIndex:])
        msgBinWithIdAndSpaces = ' '.join(listOfStingToConcatIntoMsgWithSpaces)

        return msgBinWithIdAndSpaces


    def getListOfBinValuesFromListOfHexValues(self, hexList: list) -> list:
        binList = []

        for hexFieldValue in hexList:
            binFieldValue = self.getBinStrFromHexStr(hexFieldValue)
            binList.append(binFieldValue)

        return binList


    def restoreSpacesInBinMsg(self, msgBinWithId: str) -> str:
        listOfStingToConcatIntoMsgWithSpaces = []
        beginIndex = 0

        for spaceIndex in self.listOfAllSpacesIndexes:
            adjustedSpaceIndex = (spaceIndex - self.listOfAllSpacesIndexes.index(spaceIndex)) * 4
            listOfStingToConcatIntoMsgWithSpaces.append(msgBinWithId[beginIndex: adjustedSpaceIndex])
            beginIndex = adjustedSpaceIndex

        # Adding last field
        listOfStingToConcatIntoMsgWithSpaces.append(msgBinWithId[beginIndex:])
        msgBinWithIdAndSpaces = ' '.join(listOfStingToConcatIntoMsgWithSpaces)

        return msgBinWithIdAndSpaces


    def getStrOrderedListFromList(self, listOfItems: list):
        listOfStrItems = [str(regexpIndex + 1)
                          + ". \""
                          + str(regexpTitle)
                          + "\""
                          for regexpIndex, regexpTitle in enumerate(listOfItems)]
        strList = '\n'.join(listOfStrItems)
        return strList
