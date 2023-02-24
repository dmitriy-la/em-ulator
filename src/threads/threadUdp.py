import gettext
import importlib
import os
import socket

from PyQt5.QtCore import pyqtSlot

import src.threads.threadNetworkBase as threadNetworkBase


_ = gettext.gettext


class ThreadUdp(threadNetworkBase.ThreadNetworkBase):
    def __init__(self, datalineSettings: dict, parent=None):
        threadNetworkBase.ThreadNetworkBase.__init__(self, datalineSettings, parent)

        if datalineSettings["protocolType"] == 'raw':
            self.runningRawSocket = True
            self.socketFamily = socket.AF_PACKET
            self.socketType = socket.SOCK_RAW
        else:
            self.runningRawSocket = False
            self.socketFamily = socket.AF_INET
            self.socketType = socket.SOCK_DGRAM

        self.rawMsgHandler = importlib.import_module('__profiles__.' + self.parent.profileTitle + '.handlerRawMsg')

        print("UDP Server listening", self.ownAddress)
        super().setStateIndicatorNorm()


    def run(self):
        self.initSockets()

        while self.running:
            super().sendMsgIfNeeded()

            super().receiveAndProcessMsg()

            self.sleepConstantTime()

        self.receiptDelayTimersList.clear()


    def initSockets(self) -> None:
        exception = OSError

        while exception is not None:
            try:
                self.closeSockets()

                self.recvSocket = socket.socket(self.socketFamily, self.socketType)
                print("Binding", self.ownAddress)
                self.recvSocket.bind(self.ownAddress)
                self.recvSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.recvSocket.setblocking(False)

                self.sendSocket = socket.socket(self.socketFamily, self.socketType)
                self.sendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sendSocket.setblocking(False)

                exception = None
            except socket.error as e:
                print("Socket open error", os.strerror(e.errno))
                self.closeSockets()
                self.setStateIndicatorError("Err")
            except OSError:
                self.closeSockets()
                self.setStateIndicatorError("OSerr")
            self.msleep(10)


    @pyqtSlot(str)
    def processToutAwaitingReceipt(self, msg: str) -> None:
        super().addMsgToLogger(msg, _('timeout awaiting receipt in'))
