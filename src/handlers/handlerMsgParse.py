import gettext
import re

import src.handlers.handlerMsgCreator as handlerMsgCreator
import src.handlers.handlerString as handlerString
import src.managers.managerMsgFormats as managerMsgFormats
import src.managers.managerProfiles as managerProfiles


_ = gettext.gettext


class HandlerMsgParse(object):
    def __init__(self, profileTitle: str):
        """
        :param profileTitle:
        """
        self.profileTitle = profileTitle

        self.formatManager = managerMsgFormats.ManagerMsgFormats(self.profileTitle)
        self.msgCreator = handlerMsgCreator.HandlerMsgCreator(self.profileTitle)
        self.msgTypeDict = dict()

        profileManager = managerProfiles.ManagerProfiles(self.profileTitle)
        self.maskForFormingReceiptType = profileManager.getMaskForFormingReceiptType()

        self.listRegexpForAllTypes = self.getRegexpListForAllMsgTypes()
        self.msgToParse = ''


    def getParsedMsgStrFromMsg(self, msg: str) -> str:
        """

        :param msg:
        :return:
        """
        msgType = self.getMsgTypeFromMsg(msg)

        listOfBinFieldValues = self.getListOfBinFieldValuesFromMsg(msg)

        self.msgTypeDict = self.formatManager.getInfoForMsgType(msgType)

        if self.msgTypeDict["msgTypeTitle"] == "undef":
            parsedMsg = "\n             " + _("Parse error: msg type unknown.")
        else:
            parsedMsg = "\n             " + _("Parse result") + ":\n             "
            parsedMsg += self.addParsedInfoToMsgOfType(listOfBinFieldValues, msgType)

        return parsedMsg


    def getMsgTypeFromMsg(self, msg: str) -> str:
        """

        :param msg:
        :return:
        """
        self.msgToParse = msg
        self.msgToParse = self.msgToParse.strip()

        stringHandler = handlerString.HandlerString()
        binMsgToParse = stringHandler.getWholeMsgBinStrFromHexStr(self.msgToParse)
        msgType = self.getMsgTypeFromBinMsg(binMsgToParse)

        return msgType


    def getMsgFormatDescrsFromMsg(self, msg: str) -> dict:
        """

        :param msg:
        :return:
        """
        msgType = self.getMsgTypeFromMsg(msg)
        self.msgTypeDict = self.formatManager.getInfoForMsgType(msgType)

        return self.msgTypeDict


    def getMsgWithSpacesFromReceivedNsg(self, msg: str) -> str:
        msgTypeTitle = self.getMsgTypeFromMsg(msg)
        self.msgTypeDict = self.formatManager.getInfoForMsgType(msgTypeTitle)

        if self.msgTypeDict["msgTypeTitle"] == "undef":
            return msg

        listOfBinFieldValues = self.getListOfBinFieldValuesFromMsg(msg)

        self.msgCreator.setListOfFieldValuesFromList(listOfBinFieldValues)
        msgWithSpaces = self.msgCreator.getMsgFromListOfPreviouslySetBinFieldsValuesInMsgType(msgTypeTitle)

        return msgWithSpaces


    def addParsedInfoToMsgOfType(self, listOfBinFieldValues: list, msgType: str) -> str:
        """
        :param listOfBinFieldValues:
        :param msgType:
        :return:
        """
        self.msgTypeDict = self.formatManager.getInfoForMsgType(msgType)

        if self.msgTypeDict["msgTypeTitle"] == "undef":
            parsedMsgStr = _("Parse error: msg type unknown.")
        elif self.msgTypeDict["firstFieldTitleInGroup"] != '' and self.msgTypeDict["lastFieldTitleInGroup"] != '':
            pass
            # TODO: finnish groups
            # parsedMsgStr = self.addParsedInfoToGroupedMsgOfType(listOfBinFieldValues, msgType)
            parsedMsgStr = _("Parse error: msg contains groupes. Not parseable yet.")
        else:
            parsedMsgStr = self.addParsedInfoToRegularMsgOfType(listOfBinFieldValues, msgType)

        return parsedMsgStr


    def msgTypeContainsMoreThanOneFieldOfUndefinedLength(self, fieldDescrsList) -> bool:
        undefLengthFieldsCount = 0

        if fieldDescrsList is None:
            fieldDescrsList = self.msgTypeDict["fieldDescrsList"]

        for fieldDescr in fieldDescrsList:
            fieldLength = fieldDescr["fieldLength"]
            if self.fieldLengthIsUndefined(fieldLength):
                undefLengthFieldsCount += 1

            if undefLengthFieldsCount > 1:
                return True

        return False


    def getListOfIndexesOfFieldsWithUndefLength(self, msg: str) -> list:
        msgType = self.getMsgTypeFromMsg(msg)
        self.msgTypeDict = self.formatManager.getInfoForMsgType(msgType)

        fieldDescrsList = self.msgTypeDict["fieldDescrsList"]

        listOfIndexesOfFieldsWithUndefLength = []

        for fieldIndex, fieldDescr in enumerate(fieldDescrsList):
            fieldLength = fieldDescr["fieldLength"]
            if self.fieldLengthIsUndefined(fieldLength):
                listOfIndexesOfFieldsWithUndefLength.append(fieldIndex)

        return listOfIndexesOfFieldsWithUndefLength


    def fieldLengthIsUndefined(self, fieldLength: str) -> bool:
        if fieldLength == "undef.":
            return True
        else:
            return False


    def getClosestSeparatorIndex(self, hexMsg: str, separator: str) -> int:
        """

        :param hexMsg:
        :param separator:
        :return:
        """
        hexMsgNoSpaces = hexMsg.replace(' ', '')
        hexMsgNoSpaces = hexMsgNoSpaces.upper()

        separator = separator.strip()
        separator = separator.replace(' ', '')
        separator = separator.upper()

        index = re.search(separator, hexMsgNoSpaces)

        if not index:
            return -1
        else:
            if index.start() == 0:
                index = re.search(' ', hexMsg)
            return index.start()


    def addParsedInfoToRegularMsgOfType(self, listOfBinFieldValues: list, msgTypeTitle: str) -> str:
        """

        :param listOfBinFieldValues:
        :param msgTypeTitle:
        :return:
        """
        fieldDescrsList = self.formatManager.getFieldDescrsListForMsgType(msgTypeTitle)
        lastFieldIndex = len(fieldDescrsList) - 1

        listOfBinFieldValues = list(map(self.nullifyUndefSymbol, listOfBinFieldValues))

        fieldStrList = []
        for fieldIndex, fieldDescr in enumerate(fieldDescrsList):
            binFieldStr = listOfBinFieldValues[fieldIndex]

            fieldTitle = fieldDescr["fieldTitle"]
            hexFieldStr = self.getHexFieldStrFromBinFieldStr(binFieldStr)

            fieldStrList.append(fieldTitle + '= ' + hexFieldStr + self.getMeaningStr(binFieldStr, fieldDescr))

            if fieldIndex != lastFieldIndex:
                fieldStrList.append(', ')

        parsedMsgStr = ''.join(fieldStrList)

        return parsedMsgStr


    def nullifyUndefSymbol(self, field: str) -> str:
        if 'x' in field:
            field = '0' * len(field)

        return field


    def getHexFieldStrFromBinFieldStr(self, binFieldStr: str) -> str:
        fieldLength = len(binFieldStr)
        if binFieldStr != '':
            hexFieldStr = '{:0{}X}'.format(int(binFieldStr, 2), fieldLength // 4)
        else:
            hexFieldStr = ''
        return hexFieldStr


    def getMeaningStr(self, binFieldStr: str, fieldDescr: dict) -> str:
        """

        :param binFieldStr:
        :param fieldDescr:
        :return:
        """
        meaningStr = ''

        if len(fieldDescr["fieldValuesList"]) > 0:
            meaningStr = self.getMeaningByValue(binFieldStr, fieldDescr["fieldValuesList"])
            meaningStr = ' (' + meaningStr + ')'

        return meaningStr


    def getMeaningByValue(self, binFieldStr: str, valuesList: list) -> str:
        """

        :param binFieldStr:
        :param valuesList:
        :return:
        """
        for valueAndMeaning in valuesList:
            value = int(valueAndMeaning["valueHex"], 16)
            meaningStr = valueAndMeaning["valueMeaning"]
            fieldValue = int(binFieldStr, 2)

            if value == fieldValue:
                return meaningStr

        if self.maskIsUsedForFormingReceiptType():
            receiptMaskWasAppliedToType = (int(binFieldStr, 2) & int(self.maskForFormingReceiptType, 16) ==
                                           int(self.maskForFormingReceiptType, 16))
            if receiptMaskWasAppliedToType:
                meaningStr = _('Receipt')
            else:
                meaningStr = _('Unknown Value')
        else:
            meaningStr = _('Unknown Value')

        return meaningStr


    def getRegexpListForAllMsgTypes(self) -> list:
        """

        :return:
        """
        listMsgTypes = self.formatManager.getListOfAllMsgTypeTitles()

        listMsgRegexp = []
        for msgTypeTitle in listMsgTypes:
            msgTypeDict = self.formatManager.getInfoForMsgType(msgTypeTitle)
            regexpStr = self.getRegexpFromMsgInfo(msgTypeDict)

            listMsgRegexp.append({"msgType": msgTypeTitle, "regexp": regexpStr})

        return listMsgRegexp


    def getRegexpForReceiptTypeWithMaskApplied(self) -> str:
        """

        :return:
        """
        regexpForReceiptTypeWithMaskApplied = ''

        stringHandler = handlerString.HandlerString()
        binMask = stringHandler.getWholeMsgBinStrFromHexStr(self.maskForFormingReceiptType)

        binMaskLength = len(binMask)
        for index in range(binMaskLength):
            if binMask[index] == '0':
                regexpForReceiptTypeWithMaskApplied += '[0-1]'
            elif binMask[index] == '1':
                regexpForReceiptTypeWithMaskApplied += '1'

        return regexpForReceiptTypeWithMaskApplied


    def getRegexpFromMsgInfo(self, msgTypeDict: dict) -> str:
        """
        Creates binary regular expression string for message type from message type descriptor
        :param msgTypeDict: message type descriptor
        :return regexpStr: binary string with regular expression for message type
        """
        regexpStr = '^'
        fieldDescrsList = msgTypeDict["fieldDescrsList"]

        for fieldDescr in fieldDescrsList:
            if fieldDescr["fieldLength"] == 'undef.':
                regexpStrForField = self.getRegexpStrForFieldOfUndefinedLength(msgTypeDict)
            else:
                regexpStrForField = self.getRegexpStrForFieldOfFixedLength(fieldDescr)

                if fieldDescr["fieldRole"] == 'roleType' and \
                   msgTypeDict["isReceipt"] == 'True' and \
                   self.maskIsUsedForFormingReceiptType():
                    regexpStrForField = self.getRegexpForReceiptTypeWithMaskApplied()

            regexpStr += regexpStrForField

        regexpStr += '$'

        return regexpStr


    def getRegexpStrForFieldOfUndefinedLength(self, msgTypeDict: dict) -> str:
        """
        Creates regular expression for field of undefined length.
        :param msgTypeDict:
        :return:
        """
        regexpStrForField = "((?:[0-1x]{8})*?"
        fieldDescrsList = msgTypeDict["fieldDescrsList"]

        if self.msgTypeContainsMoreThanOneFieldOfUndefinedLength(fieldDescrsList):
            stringHandler = handlerString.HandlerString()
            hexSeparator = msgTypeDict["separator"]
            binSeparator = stringHandler.getBinStrFromHexStr(hexSeparator)
            regexpStrForField += binSeparator

        regexpStrForField += ")"

        return regexpStrForField


    def getRegexpStrForFieldOfFixedLength(self, fieldDescr: dict) -> str:
        fieldLength = int(fieldDescr["fieldLength"])

        if len(fieldDescr["fieldValuesList"]) > 0:
            if fieldDescr["fieldRole"] == 'roleType':
                valueAndMeaning = fieldDescr["fieldValuesList"][0]
                regexpStrForField = "("
                hexStrValue = valueAndMeaning["valueHex"]
                binStrValue = self.getBinStrOfSpecifiedBitLenFromHexStr(hexStrValue, fieldLength)
                regexpStrForField += binStrValue
                regexpStrForField += "){1}"
            else:
                regexpStrForField = "([0-1x]{" + str(fieldLength) + "})"
        else:
            regexpStrForField = "([0-1x]{" + str(fieldLength) + "})"

        return regexpStrForField


    def getBinStrOfSpecifiedBitLenFromHexStr(self, hexStr: str, bitLen=-1) -> str:
        """

        :param hexStr:
        :param bitLen:
        :return:
        """
        listOfHexFields = hexStr.split(' ')
        binStr = ''

        for hexFieldStr in listOfHexFields:
            if hexFieldStr != '':
                binFieldStr = '{:0{}b}'.format(int(hexFieldStr, 16), len(hexFieldStr))
                binStr += binFieldStr + ' '

        binStr = binStr[:-1]

        if bitLen > 0:
            binStr = binStr.zfill(bitLen)

        return binStr


    def getMsgTypeFromBinMsg(self, binMsg: str) -> str:
        """

        :param binMsg:
        :return:
        """
        self.msgToParse = binMsg
        self.msgToParse = self.msgToParse.strip()

        binMsg = binMsg.replace(" ", "")

        for regexpAndType in self.listRegexpForAllTypes:
            regexp = regexpAndType["regexp"]
            result = re.search(regexp, binMsg)
            if result:
                msgType = regexpAndType["msgType"]
                return msgType

        # print('msgType NOT FOUND!')

        return ''


    def setFieldValueInMsg(self, msg: str, fieldTitle: str, newValue: str) -> str:
        listOfBinFieldValues = self.getListOfBinFieldValuesFromMsg(msg)

        msgTypeTitle = self.getMsgTypeFromMsg(msg)

        fieldIndex = self.formatManager.getFieldIndexByTitleInMsgType(msgTypeTitle, fieldTitle)
        if fieldIndex is None:
            return msg

        strHandler = handlerString.HandlerString()
        newValueBin = strHandler.getBinStrFromHexStr(newValue)

        listOfBinFieldValues[fieldIndex] = newValueBin

        self.msgCreator.setListOfFieldValuesFromList(listOfBinFieldValues)
        msg = self.msgCreator.getMsgFromListOfPreviouslySetBinFieldsValuesInMsgType(msgTypeTitle)

        return msg


    def getIdFromMsg(self, msg: str) -> str:
        """

        :param msg:
        :return:
        """
        idFromMsg = ""

        msgTypeTitle = self.getMsgTypeFromMsg(msg)
        idFieldIndex = self.formatManager.getIndexOfFieldWithRoleIdInMsgType(msgTypeTitle)

        if idFieldIndex is None or msgTypeTitle == "":
            return ""

        stringHandler = handlerString.HandlerString()
        binMsg = stringHandler.getWholeMsgBinStrFromHexStr(msg)
        binMsg = binMsg.replace(' ', '')

        regexp = self.getRegexpFromMsgTypeTitle(msgTypeTitle)

        result = re.search(regexp, binMsg)
        if result:
            idFromMsg = result.group(idFieldIndex + 1)

        return idFromMsg


    def getRegexpFromMsgTypeTitle(self, msgTypeTitle: str):
        for regexpAndType in self.listRegexpForAllTypes:
            if regexpAndType["msgType"] == msgTypeTitle:
                return regexpAndType["regexp"]


    def getListOfBinFieldValuesFromMsg(self, msg) -> list:
        """

        :param msg:
        :return:
        """
        listOfFieldValues = []

        self.msgTypeDict = self.getMsgDictFromMsg(msg)

        if self.msgTypeDict is None or self.msgTypeDict["msgTypeTitle"] == "undef":
            return list()

        stringHandler = handlerString.HandlerString()
        binMsg = stringHandler.getWholeMsgBinStrFromHexStr(msg)
        binMsg = binMsg.replace(' ', '')

        for regexpAndType in self.listRegexpForAllTypes:
            regexp = regexpAndType["regexp"]
            result = re.search(regexp, binMsg)
            if result:
                listOfFieldValues = list(result.groups())

        return listOfFieldValues


    def prepareMsg(self, msg) -> str:
        """

        :param msg:
        :return:
        """
        if isinstance(msg, bytes):
            msg = msg.decode('utf-8', 'replace')

        msg = msg.strip('b\'')
        msg = msg.replace('\\x', '')
        msg = msg.replace('\'', '')

        return msg


    def getMsgDictFromMsg(self, msg: str) -> dict:
        """

        :param msg:
        :return:
        """
        msgType = self.getMsgTypeFromMsg(msg)

        msgTypeDict = self.formatManager.getInfoForMsgType(msgType)

        return msgTypeDict


    def msgIsReceipt(self, msg: str) -> bool:
        """

        :param msg:
        :return:
        """
        msgIsReceipt = False

        # if self.maskIsUsedForFormingReceiptType():
        #     msgIsReceipt = self.receiptMaskWasAppliedToMsgType(msg)
        # else:
        msgIsReceipt = self.msgMarkedAsReceipt(msg)

        return msgIsReceipt


    def msgMarkedAsReceipt(self, msg) -> bool:
        """

        :param msg:
        :return:
        """
        msgTypeTitle = self.getMsgTypeFromMsg(msg)

        msgIsReceipt = self.formatManager.getIfMsgTypeIsReceipt(msgTypeTitle)

        return msgIsReceipt


    def maskIsUsedForFormingReceiptType(self) -> bool:
        """

        :return:
        """
        if self.maskForFormingReceiptType != '':
            return True
        else:
            return False
