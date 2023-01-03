from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QDialog

import handlers.handlerCrc
import handlers.handlerMsgCreator
import handlers.handlerMsgLength
import handlers.handlerMsgParse
import handlers.handlerString
import managers.managerDatalineSettings
import managers.managerMsgFormats
import managers.managerProfiles
import threads


class HandlerReceipting(QObject):
    signalResendMsg = pyqtSignal(str)
    signalToutAwaitingReceipt = pyqtSignal(str)

    def __init__(self, profileTitle: str, datalineTitle="default", callbackResend=None, callbackTimeout=None):
        super().__init__()
        self.profileTitle = profileTitle
        self.datalineTitle = datalineTitle
        self.callbackFunctionForMsgResend = callbackResend
        self.callbackFunctionForReceiptTimeout = callbackTimeout

        self.listOfAllMsgTypesInfo = []

        self.listOfMsgsThatAwaitReceipts = []

        self.listOfBinFieldValues = []

        self.formatsManager = managers.managerMsgFormats.ManagerMsgFormats(self.profileTitle)
        self.msgReceiptDict = self.formatsManager.getInfoForReceiptMsg()

        self.parser = handlers.handlerMsgParse.HandlerMsgParse(self.profileTitle)

        self.managerDatalineSettings = managers.managerDatalineSettings.ManagerDatalineSettings(profileTitle)
        self.datalineSettings = self.managerDatalineSettings.getDatalineSettingsByDatalineTitle(datalineTitle)

        self.receiptToutMs = self.datalineSettings["toutMs"]
        self.resendRepeats = self.datalineSettings["repeats"]
        self.receiptDelay = self.datalineSettings["delay"]

        self.setSettingsFilePathsForProfile(self.profileTitle)

        profileManager = managers.managerProfiles.ManagerProfiles(self.profileTitle)
        self.maskForFormingReceiptType = profileManager.getMaskForFormingReceiptType()
        self.sendMode = profileManager.getSendMode()


    def setSettingsFilePathsForProfile(self, profileTitle: str) -> None:
        self.formatsManager.setCurrentProfile(profileTitle)

        allMsgTypes = self.formatsManager.getListOfAllMsgTypeTitles()

        for msgType in allMsgTypes:
            msgTypeDict = self.formatsManager.getInfoForMsgType(msgType)
            self.listOfAllMsgTypesInfo.append(msgTypeDict)


    def getReceiptForMsg(self, msg: str) -> str:
        if self.receiptForMsgIsRetrievable(msg):
            self.listOfBinFieldValues = self.parser.getListOfBinFieldValuesFromMsg(msg)

            fieldDescrsList = self.msgReceiptDict["fieldDescrsList"]

            for fieldIndex, fieldDescr in enumerate(fieldDescrsList):
                self.proccessFieldDescrInReceipt(fieldIndex, fieldDescr)

            msgTypeTitle = self.msgReceiptDict["msgTypeTitle"]
            msgCreator = handlers.handlerMsgCreator.HandlerMsgCreator(self.profileTitle)
            msgCreator.setListOfFieldValuesFromList(self.listOfBinFieldValues)
            receipt = msgCreator.getMsgFromListOfPreviouslySetBinFieldsValuesInMsgType(msgTypeTitle)

            msgLengthHandler = handlers.handlerMsgLength.HandlerMsgLength(self.profileTitle)
            receipt = msgLengthHandler.setLengthInMsg(receipt)

            crcHandler = handlers.handlerCrc.HandlerCrc(self.profileTitle)
            receipt = crcHandler.getMsgWithCrc(receipt)
        else:
            receipt = msg

        return receipt


    def receiptForMsgIsRetrievable(self, msg: str) -> bool:
        msgIsReceipt = self.parser.msgIsReceipt(msg)
        msgTypeDictIsAbsent = self.msgReceiptDict is None or self.msgReceiptDict["msgTypeTitle"] == "undef"
        msgIsNotParsable = len(self.parser.getListOfBinFieldValuesFromMsg(msg)) <= 0

        fieldDescrsList = self.msgReceiptDict["fieldDescrsList"]
        fieldDescrsListCount = len(fieldDescrsList)
        binFieldValuesListCount = len(self.listOfBinFieldValues)
        fieldDescrListDoesntMatchFieldValuesList = fieldDescrsListCount != binFieldValuesListCount and\
                                                   self.msgReceiptDict["isReceipt"] is False

        if msgIsReceipt or msgTypeDictIsAbsent or msgIsNotParsable or fieldDescrListDoesntMatchFieldValuesList:
            # print("Receipt is not retrievable.")
            return False
        else:
            return True


    def proccessFieldDescrInReceipt(self, fieldIndex: int, fieldDescr: dict) -> None:
        fieldRole = fieldDescr["fieldRole"]

        if fieldIndex < len(self.listOfBinFieldValues):
            if fieldRole == 'roleType':
                binFieldValue = self.getBinFieldValueForFieldWithRoleType(fieldDescr, fieldIndex)
                self.listOfBinFieldValues[fieldIndex] = binFieldValue
            elif fieldRole == 'roleLength':
                binFieldValue = self.getBinFieldValueForFieldWithRoleLength(fieldIndex)
                self.listOfBinFieldValues[fieldIndex] = binFieldValue
            elif fieldRole == 'roleCrc':
                binFieldValue = self.getBinFieldValueForFieldWithRoleCrc(fieldIndex)
                self.listOfBinFieldValues[fieldIndex] = binFieldValue


    def getBinFieldValueForFieldWithRoleCrc(self, fieldIndex: int) -> str:
        if fieldIndex < len(self.listOfBinFieldValues):
            binFieldValue = '0'.zfill(len(self.listOfBinFieldValues[fieldIndex]))
        else:
            binFieldValue = '0'

        return binFieldValue


    def getBinFieldValueForFieldWithRoleLength(self, fieldIndex: int) -> str:
        msgType = self.msgReceiptDict["msgTypeTitle"]
        msgLen = self.formatsManager.getMsgLengthByMsgType(msgType)
        binFieldValue = '{:0{}b}'.format(msgLen, len(self.listOfBinFieldValues[fieldIndex]))

        return binFieldValue


    def getBinFieldValueForFieldWithRoleType(self, fieldDescr: dict, fieldIndex: int) -> str:
        strHandler = handlers.handlerString.HandlerString()

        if self.maskForFormingReceiptType != "":
            intTypeWithMask = int(self.listOfBinFieldValues[fieldIndex], 16) | int(self.maskForFormingReceiptType, 16)
            hexStrTypeWithMask = '{:0{}X}'.format(intTypeWithMask, len(self.listOfBinFieldValues[fieldIndex]))
            binFieldValue = strHandler.getBinStrFromHexStr(hexStrTypeWithMask)
        else:
            hexFieldValue = fieldDescr["fieldValuesList"][0]["valueHex"]
            binFieldValue = strHandler.getBinStrFromHexStr(hexFieldValue)

        return binFieldValue


    def startTimerForReceiptForMsg(self, msgSent: str) -> None:
        if self.parser.msgIsReceipt(msgSent):
            return

        msgId = self.getIdFromMsg(msgSent)

        if not self.alreadyProcessingMsgWithId(msgId):
            repsCount = 0
            receiptTimer = threads.threadTimer.ThreadTimer(self.proccesTimeoutSignalForMsgWithId, msgId,
                                                           self.receiptToutMs, self.resendRepeats)

            dictForTrackingMsgsAndReceipts = {"msgId":        msgId,
                                              "msgSent":      msgSent,
                                              "receiptTimer": receiptTimer,
                                              "repsCount":    repsCount}

            self.listOfMsgsThatAwaitReceipts.append(dictForTrackingMsgsAndReceipts)


    def stopTimerForMsgWithId(self, msgId: str) -> None:
        for msgInfo in self.listOfMsgsThatAwaitReceipts:
            if msgInfo["msgId"] == msgId:
                self.listOfMsgsThatAwaitReceipts.remove(msgInfo)


    def alreadyProcessingMsgWithId(self, msgId: str) -> bool:
        for msgInfo in self.listOfMsgsThatAwaitReceipts:
            if msgInfo["msgId"] == msgId:
                return True

        return False


    def getIdFromMsg(self, msg: str) -> str:
        msgId = self.parser.getIdFromMsg(msg)

        return msgId


    def proccessReceivedMsg(self, msgReceived: str) -> str:
        if self.parser.msgIsReceipt(msgReceived):
            msgId = self.getIdFromMsg(msgReceived)

            self.stopTimerForMsgWithId(msgId)
            # print("No receipt for receipt.")
            return ''
        else:
            receipt = self.getReceiptForMsg(msgReceived)
            crcHandler = handlers.handlerCrc.HandlerCrc(self.profileTitle)
            receipt = crcHandler.getMsgWithCrc(receipt)

            # print("Receipt:", receipt)
            return receipt


    def proccesTimeoutSignalForMsgWithId(self, msgId: str) -> None:
        self.incrRepsCountForMsgWithId(msgId)

        repsCount = self.getRepsCountForMsgWithId(msgId)

        msg = self.getMsgById(msgId)

        if repsCount < self.resendRepeats:
            self.notifyAboutResending(msg)
        elif repsCount > 0:
            self.notifyAboutTimeout(msg)
            self.stopTimerForMsgWithId(msgId)


    def notifyAboutResending(self, msgToResend: str) -> None:
        if self.callbackFunctionForMsgResend is None:
            # print("Resend signal")
            self.signalResendMsg.emit(msgToResend)
        else:
            # print("Resend callback")
            self.callbackFunctionForMsgResend(msgToResend)


    def notifyAboutTimeout(self, msgToResend: str) -> None:
        if self.callbackFunctionForReceiptTimeout is None:
            print("Timeout signal")
            self.signalToutAwaitingReceipt.emit(msgToResend)
        else:
            print("Timeout callback")
            self.callbackFunctionForReceiptTimeout(msgToResend)


    def stillWaitingReceipts(self) -> bool:
        if len(self.listOfMsgsThatAwaitReceipts) > 0:
            return True
        else:
            return False


    def getRepsCountForMsgWithId(self, msgId: str) -> int:
        for msgInfo in self.listOfMsgsThatAwaitReceipts:
            if msgInfo["msgId"] == msgId:
                return msgInfo["repsCount"]
        return -1


    def incrRepsCountForMsgWithId(self, msgId: str) -> int:
        for msgInfo in self.listOfMsgsThatAwaitReceipts:
            if msgInfo["msgId"] == msgId:
                msgInfo["repsCount"] += 1
        return -1


    def getMsgById(self, msgId: str) -> str:
        for msgInfo in self.listOfMsgsThatAwaitReceipts:
            if msgInfo["msgId"] == msgId:
                return msgInfo["msgSent"]


    def updateReceiptingSettings(self) -> None:
        # print("updating receipting settings")
        self.managerDatalineSettings.readDatalineSettingsList()
        datalineTitle = self.datalineSettings["title"]
        self.datalineSettings = self.managerDatalineSettings.getDatalineSettingsByDatalineTitle(datalineTitle)

        self.receiptToutMs = self.datalineSettings["toutMs"]
        self.resendRepeats = self.datalineSettings["repeats"]
        self.receiptDelay = self.datalineSettings["delay"]

        # print("Timeout:", self.receiptToutMs, "repeats:", self.resendRepeats)


    def getLenOfReceiptInBytes(self, msgReceipt: str) -> int:
        """
        :return:
        """
        msgReceipt = msgReceipt.replace(' ', '')
        msgReceiptLen = len(msgReceipt) // 2

        currentMsgType = self.parser.getMsgTypeFromMsg(msgReceipt)
        excludedLength = self.formatManager.getLengthOfFieldExcludedFromLenCountInMsgType(currentMsgType)
        msgReceiptLen -= excludedLength // 8

        if msgReceiptLen <= 0:
            msgReceiptLen = self.formatManager.getMsgLengthByMsgType(currentMsgType)

        return msgReceiptLen