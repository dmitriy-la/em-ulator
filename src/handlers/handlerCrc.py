import importlib

import src.handlers.handlerMsgParse as handlerMsgParse
import src.handlers.handlerString as handlerString
import src.managers.managerMsgFormats as managerMsgFormats


class HandlerCrc(object):
    def __init__(self, profileTitle: str):
        """
        Module that encapsulates all work with control sums in messages
        :param profileTitle:
        """
        self.profileTitle = profileTitle

        self.formatManager = managerMsgFormats.ManagerMsgFormats(self.profileTitle)

        self.calcCrcModule = importlib.import_module('__profiles__.' + self.profileTitle + '.calcCrc')


    def getMsgWithUndefCrc(self, msgWithoutCrc: str) -> str:
        crc = 'x'

        msgHexWithCrcAndSpaces = self.setCrcInMsg(msgWithoutCrc, crc)

        return msgHexWithCrcAndSpaces


    def getMsgWithCrc(self, msgWithoutCrc: str) -> str:
        hexCrc = self.calcCrcModule.calcCrc(self, msgWithoutCrc)

        msgHexWithCrc = self.setCrcInMsg(msgWithoutCrc, hexCrc)

        if msgHexWithCrc == "":
            print("ERROR: error assigning crc")
            msgHexWithCrc = msgWithoutCrc

        return msgHexWithCrc


    def setCrcInMsg(self, msgWithoutCrc: str, hexCrc: str) -> str:
        if self.hexCrcIsValid(hexCrc) and self.msgIsParsable(msgWithoutCrc):
            parser = handlerMsgParse.HandlerMsgParse(self.profileTitle)
            msgType = parser.getMsgTypeFromMsg(msgWithoutCrc)

            crcFieldIndex = self.formatManager.getIndexOfFieldWithRoleCrcInMsgType(msgType)
            crcFieldLen = self.formatManager.getLengthOfFieldWithRoleCrcInMsgType(msgType)

            stringHandler = handlerString.HandlerString()
            strCrc = stringHandler.getBinaryStringOfSpecifiedBitLen(hexCrc, crcFieldLen)
            strCrc = strCrc.zfill(crcFieldLen)

            listOfBinValues = parser.getListOfBinFieldValuesFromMsg(msgWithoutCrc)
            if crcFieldIndex is not None:
                listOfBinValues[crcFieldIndex] = strCrc

            msgHexWithCrc = stringHandler.getHexStrFromBinList(listOfBinValues)
            return msgHexWithCrc
        else:
            return msgWithoutCrc


    def hexCrcIsValid(self, hexCrc: str) -> bool:
        if (hexCrc is not None) and (hexCrc != ""):
            return True
        else:
            return False


    def msgIsParsable(self, msg) -> bool:
        parser = handlerMsgParse.HandlerMsgParse(self.profileTitle)
        listOfBinValues = parser.getListOfBinFieldValuesFromMsg(msg)

        if len(listOfBinValues) > 0:
            return True
        else:
            return False


    def checkCrcInReceivedMsg(self, msgWithoutCrc: str, crcInMsg: str) -> bool:
        hexCrc = self.calcCrcModule.calcCrc(self, msgWithoutCrc)

        if hexCrc == crcInMsg:
            return True
        else:
            return False
