import src.handlers.handlerMsgParse as handlerMsgParse
import src.handlers.handlerString as handlerString
import src.managers.managerMsgFormats as managerMsgFormats


class HandlerId(object):
    def __init__(self, profileTitle: str):
        self.profileTitle = profileTitle

        self.listOfAllSpacesIndexes = []

        self.formatsManager = managerMsgFormats.ManagerMsgFormats(self.profileTitle)


    def setUndefIdInMsg(self, msgWithoutId: str) -> str:
        idForMsg = 'x'
        msgWithUndefId = self.setIdInMsg(msgWithoutId, idForMsg)

        return msgWithUndefId


    def setIdInMsg(self, msgWithoutId: str, idForMsg) -> str:
        stringHandler = handlerString.HandlerString()

        parser = handlerMsgParse.HandlerMsgParse(self.profileTitle)
        listOfBinValues = parser.getListOfBinFieldValuesFromMsg(msgWithoutId)

        msgType = parser.getMsgTypeFromMsg(msgWithoutId)
        idFieldIndex = self.formatsManager.getIndexOfFieldWithRoleIdInMsgType(msgType)

        if idFieldIndex > 0:
            idFieldLen = len(listOfBinValues[idFieldIndex])
            strId = stringHandler.getBinaryStringOfSpecifiedBitLen(idForMsg, idFieldLen)

            listOfBinValues[idFieldIndex] = strId

        msgHexWithId = stringHandler.getHexStrFromBinList(listOfBinValues)

        if msgHexWithId == "":
            return msgWithoutId
        else:
            return msgHexWithId
