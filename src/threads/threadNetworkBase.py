import gettext
import os
import socket

from PyQt5.QtCore import QThread, pyqtSignal

import src.handlers.handlerReceipting as handlerReceipting
import src.threads.threadTimer as threadTimer


_ = gettext.gettext


class ThreadNetworkBase(QThread):
    signalSetStateLabelNorm = pyqtSignal(str)
    signalSetStateLabelError = pyqtSignal(str, str)

    def __init__(self, datalineSettings: dict, parent=None):
        QThread.__init__(self)
        self.parent = parent
        self.datalineSettings = datalineSettings

        self.ownAddress = (datalineSettings["ipOwn"], datalineSettings["portOwn"])
        self.sendAddress = (datalineSettings["ipSend"], datalineSettings["portSend"])

        self.clientAddress = self.sendAddress

        self.recvSocket = None
        self.sendSocket = None

        self.receipting = self.getReceiptingModule()

        self.msgToBeSentList = self.parent.msgToBeSentList

        self.receiptDelayTimersList = []

        self.msgForWhichWaitingReceipt = ''

        self.receiptDelayTimersList = []

        self.sendMode = self.parent.sendMode

        self.connected = False


    def getReceiptingModule(self):
        if self.datalineSettings["protocolType"] == "TCP-server":
            receiptingHandlerArgs = [self.parent.profileTitle, self.parent.title, self.sendMsg,
                                     self.processToutAwaitingReceipt]
            self.receipting = handlerReceipting.HandlerReceipting(*receiptingHandlerArgs)
        else:
            receiptingHandlerArgs = [self.parent.profileTitle, self.datalineSettings["title"]]
            self.receipting = handlerReceipting.HandlerReceipting(*receiptingHandlerArgs)
            self.receipting.signalResendMsg.connect(self.sendMsg)
            self.receipting.signalToutAwaitingReceipt.connect(self.processToutAwaitingReceipt)

        return self.receipting


    def closeSockets(self) -> None:
        self.connected = False

        if self.sendSocket is not None:
            self.sendSocket.close()

        if self.recvSocket is not None:
            self.recvSocket.close()


    def updateReceiptingSettings(self) -> None:
        self.receipting.updateReceiptingSettings()


    def sendMsgIfNeeded(self) -> None:
        if self.thereAreMessagesToSend():
            if self.sendingAllowed():
                self.sendAllMessages()
            else:
                self.proccessSequentialSending()


    def thereAreMessagesToSend(self) -> bool:
        if len(self.msgToBeSentList) > 0:
            return True
        else:
            return False


    def sendingAllowed(self) -> bool:
        # In sequential mode next message is only being sent
        # after getting receipt for the previous message
        if not (self.sequentialSendMode() and self.receipting.stillWaitingReceipts()):
            return True
        else:
            return False


    def sendAllMessages(self) -> None:
        for msgToSend in self.msgToBeSentList:
            self.parent.responseManager.proccessMsgSent(msgToSend)
            self.sendMsg(msgToSend)


    def sequentialSendMode(self) -> bool:
        if self.parent.sendMode == 'sequential':
            return True
        else:
            return False


    def sendMsg(self, msgToSend: str) -> None:
        msgToSendIsNotEmpty = (msgToSend != "" and msgToSend is not None)

        if msgToSendIsNotEmpty:
            print("Sending:", msgToSend, 'from', self.ownAddress)
            try:
                msgToSend = self.createPacketForMsgInRawSocketIfNeeded(msgToSend)
                msgHexBytes = self.prepareMsg(msgToSend)

                res = self.sendToSocket(msgHexBytes)

                loggerCommentStr = self.getLoggerCommentStr(res)
                self.parent.addMsgToLogger(msgToSend, loggerCommentStr)

                self.removeMsgFromSendingList(msgToSend)

                self.receipting.startTimerForReceiptForMsg(msgToSend)
            except BrokenPipeError:
                self.processSocketError(_('ERR'), "BrokenPipeError")

                print("Send error: ", "BrokenPipeError")
            except ConnectionResetError:
                self.processSocketError(_('ERR'), "ConnectionResetError")

                print("Send error: ", "ConnectionResetError")
            except ConnectionError:
                self.processSocketError(_('ERR'), "ConnectionError")

                print("Send error: ", "ConnectionError")
            except socket.error as e:
                errorStr = _("Error: ") + os.strerror(e.errno)

                self.processSocketError(_('ERR'), errorStr)

                print("Send error: ", errorStr)
            except OSError:
                self.processSocketError(_('ERR'), "OSError")

                print("Send error: ", "OSError")


    def sendToSocket(self, msgHexBytes: bytes) -> int:
        if self.datalineSettings["protocolType"] == "UDP" or self.datalineSettings["protocolType"] == "raw":
            res = self.sendSocket.sendto(msgHexBytes, self.clientAddress)
        else:
            res = self.sendSocket.send(msgHexBytes)
        return res


    def createPacketForMsgInRawSocketIfNeeded(self, msgToSend):
        if self.datalineSettings["protocolType"] == "raw":
            msgToSend = self.rawMsgHandler.proccessMsgForSend(self, msgToSend)

        return msgToSend


    def prepareMsg(self, msgToSend: str) -> bytes:
        if isinstance(msgToSend, bytes):
            msgToSend = msgToSend.decode('utf-8', 'replace')
        else:
            msgToSend = str(msgToSend.strip())
            msgToSend = msgToSend.strip('b\'')
            msgToSend = msgToSend.replace('\\x', '')
            msgToSend = msgToSend.replace('\'', '')
            msgToSend = msgToSend.replace(' ', '')

        if 'x' in msgToSend:
            msgToSend = msgToSend.replace('x', '0')

        msgHex = msgToSend.encode('utf-8')

        return msgHex


    def getLoggerCommentStr(self, res: int) -> str:
        if res > 0:
            loggerCommentStr = _('sent from')
        else:
            loggerCommentStr = _('send error')

        return loggerCommentStr


    def removeMsgFromSendingList(self, msgToSend) -> None:
        if msgToSend in self.msgToBeSentList:
            self.msgToBeSentList.remove(msgToSend)


    def proccessSequentialSending(self) -> None:
        lastSuccessfullySentMsg = self.receipting.listOfMsgsThatAwaitReceipts[0]["msgSent"]

        if self.msgForWhichWaitingReceipt != lastSuccessfullySentMsg:
            self.parent.addMsgToLogger(lastSuccessfullySentMsg, _('no receipt for previously sent msg'))
            self.msgForWhichWaitingReceipt = lastSuccessfullySentMsg

            self.removeMsgFromSendingList(lastSuccessfullySentMsg)


    def receiveAndProcessMsg(self) -> None:
        data = self.receiveMsg()

        if self.receivedValidData(data):
            self.parent.addMsgToLogger(data, _('received in'))

            msgReceived = data
            self.addReceiptToSendingListIfNeeded(msgReceived)
            self.addListOfResponsesToSendingListIfNeeded(msgReceived)


    def receiveMsg(self):
        buf_size = 1024
        data = None

        try:
            data = self.recvSocket.recv(buf_size)
        except BlockingIOError:
            pass
            # print("Blocking err")
        except BrokenPipeError:
            self.processSocketError(_('ERR'), "BrokenPipeError")

            print("Recv error: ", "BrokenPipeError")
        except ConnectionResetError:
            self.processSocketError(_('ERR'), "ConnectionResetError")

            print("Recv error: ", "ConnectionResetError")
        except socket.error as e:
            errorStr = os.strerror(e.errno)
            errorStr += _(" error")

            self.processSocketError(_('ERR'), errorStr)

            print("Recv error: ", errorStr)
        except OSError:
            self.processSocketError(_('ERR'), "OSError")

            print("Recv error: ", "OSError")

        return data


    def addListOfResponsesToSendingListIfNeeded(self, msgReceived: str) -> None:
        listOfMsgAsResponse = self.parent.responseManager.proccessMsgReceived(msgReceived)
        self.parent.addListOfMsgToSendingList(listOfMsgAsResponse)


    def addReceiptToSendingListIfNeeded(self, msgReceived: str) -> None:
        receipt = self.receipting.proccessReceivedMsg(msgReceived)

        if receipt != '' and self.parent.receiptOn:
            timerArgs = [self.sendMsg, receipt, self.receipting.receiptDelay]
            receiptDelayTimer = threadTimer.ThreadTimer(*timerArgs)
            self.receiptDelayTimersList.append(receiptDelayTimer)

            self.removeFinishedReceiptDelayTimersFromTimersList()


    def removeFinishedReceiptDelayTimersFromTimersList(self) -> None:
        for timer in self.receiptDelayTimersList:
            if timer.isFinished():
                self.receiptDelayTimersList.remove(timer)


    def receivedValidData(self, data) -> bool:
        if (data is not None) and (str(data) != "b\'\'") and str(data) != "":
            return True
        else:
            return False


    def setStateIndicatorError(self, error: str) -> None:
        self.parent.labelNetStateCurrent.setText(error)
        self.parent.labelNetStateCurrent.setStyleSheet('QLabel {background-color : red; }')


    def setStateIndicatorNorm(self) -> None:
        self.parent.labelNetStateCurrent.setText(_('Norm'))
        self.parent.labelNetStateCurrent.setStyleSheet('QLabel {background-color : limegreen; }')


    def processSocketError(self, stateStrShort: str, stateStrFull='') -> None:
        self.connected = False

        self.parent.addMsgToLogger('', stateStrFull + _(" in"))

        self.signalSetStateLabelError.emit(stateStrShort, stateStrFull)

        print(stateStrFull)
