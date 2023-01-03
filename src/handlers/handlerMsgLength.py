import handlers.handlerMsgParse
import handlers.handlerString
import managers.managerMsgFormats


class HandlerMsgLength(object):
    def __init__(self, profileTitle: str):
        self.profileTitle = profileTitle

        self.listOfAllSpacesIndexes = []

        self.parser = handlers.handlerMsgParse.HandlerMsgParse(self.profileTitle)

        self.formatManager = managers.managerMsgFormats.ManagerMsgFormats(self.profileTitle)


    def setLengthInMsg(self, msgHex: str) -> str:
        stringHandler = handlers.handlerString.HandlerString()

        parser = handlers.handlerMsgParse.HandlerMsgParse(self.profileTitle)
        listOfBinValues = parser.getListOfBinFieldValuesFromMsg(msgHex)

        msgType = parser.getMsgTypeFromMsg(msgHex)
        lengthFieldIndex = self.formatManager.getIndexOfFieldWithRoleLengthInMsgType(msgType)

        msgLengthInBytes = self.getLenOfMsgInBytes(msgHex)

        if lengthFieldIndex >= 0:
            lengthFieldLen = len(listOfBinValues[lengthFieldIndex])
            strLength = stringHandler.getBinaryStringOfSpecifiedBitLen(msgLengthInBytes, lengthFieldLen)

            listOfBinValues[lengthFieldIndex] = strLength

        msgHexWithLength = stringHandler.getHexStrFromBinList(listOfBinValues)

        if msgHexWithLength == "":
            return msgHex
        else:
            return msgHexWithLength


    def getLenOfMsgInBytes(self, msg: str) -> int:
        """
        :return:
        """
        msg = msg.replace('MSG (bin): ', '')
        msg = msg.replace('MSG: ', '')
        msg = msg.replace(' ', '')
        msgLen = len(msg) // 2

        currentMsgType = self.parser.getMsgTypeFromMsg(msg)
        excludedLength = self.formatManager.getLengthOfFieldExcludedFromLenCountInMsgType(currentMsgType)
        msgLen -= excludedLength // 8

        if msgLen <= 0:
            msgLen = self.formatManager.getMsgLengthByMsgType(currentMsgType)

        return msgLen