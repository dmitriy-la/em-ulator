import gettext
import os
import socket

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

import threads.threadTimer
import threads.threadNetworkBase

_ = gettext.gettext


class ThreadForSingleTcpClientInTcpServer(threads.threadNetworkBase.ThreadNetworkBase):
    def __init__(self, datalineSettings: dict, clientSocket, threadIndex: int, parent=None):
        threads.threadNetworkBase.ThreadNetworkBase.__init__(self, datalineSettings, parent)
        self.ip = datalineSettings["ipOwn"]
        self.port = datalineSettings["portOwn"]
        self.recvSocket = clientSocket
        self.sendSocket = clientSocket
        self.threadIndex = threadIndex

        self.connected = True

        self.msgToBeSentList = []


    def run(self):
        while self.connected or self.receipting.stillWaitingReceipts():
            self.sendMsgIfNeeded()
            self.receiveAndProcessMsg()
            self.msleep(1)

        self.stopThreadForSingleClient()


    def addMsgToBeSent(self, msgToSend: str) -> None:
        self.msgToBeSentList.append(msgToSend)


    def stopThreadForSingleClient(self) -> None:
        self.recvSocket.close()

        self.connected = False

        if self in self.parent.listClientThreads:
            self.parent.listClientThreads.remove(self)

        self.parent.setStateLabelNorm(_("Norm, clients: ") + str(len(self.parent.listClientThreads)))
        self.parent.addMsgToLogger('', _("Connection with client ") + self.ip + "," + str(self.port) + _(" stopped in"))

        self.receiptDelayTimersList.clear()

        print("Thread for client terminated.")


    @pyqtSlot(str)
    def processToutAwaitingReceipt(self, msg: str) -> None:
        print("Process receipt tout")
        self.parent.addMsgToLogger(msg, _('Sending failed: receipt timeout'))

        if self.parent.consecutiveSendingToClients():
            self.addMsgsForSendingToNextClient(msg)


    def addMsgsForSendingToNextClient(self, msg: str) -> None:
        """
        If emulated dataline is supposed to work only with one client at a time
        and switch to the next client only after losing connection with the current one -
        then this method switches dataline to the next client.
        :param msg:
        :return:
        """
        nextClientThreadIndex = self.getNextClientThreadIndex()
        self.parent.currentClientThread = nextClientThreadIndex

        listClientThreads = self.parent.listClientThreads

        listClientThreads[nextClientThreadIndex].addMsgToBeSent(msg)


    def getNextClientThreadIndex(self) -> int:
        listClientThreads = self.parent.listClientThreads
        nextClientThreadIndex = self.threadIndex + 1
        maxIndexInListClientThreads = len(listClientThreads) - 1

        if nextClientThreadIndex > maxIndexInListClientThreads:
            nextClientThreadIndex = 0

        return nextClientThreadIndex
