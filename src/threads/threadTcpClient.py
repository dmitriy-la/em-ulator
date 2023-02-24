import gettext
import os
import socket

from PyQt5.QtCore import pyqtSignal, pyqtSlot

import src.threads.threadNetworkBase as threadNetworkBase

_ = gettext.gettext


class ThreadTcpClient(threadNetworkBase.ThreadNetworkBase):
    signalSetStateLabelNorm = pyqtSignal(str)
    signalSetStateLabelError = pyqtSignal(str, str)

    def __init__(self, datalineSettings: dict, parent=None):
        threadNetworkBase.ThreadNetworkBase.__init__(self, datalineSettings, parent)


    def initSockets(self) -> None:
        self.recvSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.recvSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.recvSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self.sendSocket = self.recvSocket


    def closeSockets(self) -> None:
        self.recvSocket.close()


    def run(self):
        self.initSockets()

        while self.stillRunning():
            self.sleepConstantTime()
            if self.connected:
                super().sendMsgIfNeeded()
                super().receiveAndProcessMsg()
            else:
                self.connectingToServer(self.sendAddress)
        else:
            print("Client stopped")
            self.receiptDelayTimersList.clear()


    def stillRunning(self):
        if self.parent is None:
            return True
        else:
            return self.parent.running


    def connectingToServer(self, address: tuple) -> None:
        print("Connecting", address)

        while self.running and not self.connected:
            try:
                self.closeSockets()
                self.initSockets()
                self.attemptConnectToServer(address)
            except socket.error as e:
                errorStr = os.strerror(e.errno)
                errorStr += _(" error")
                self.processConnectError(_('ERR'), errorStr)
                print("Connect error: ", errorStr)
            self.msleep(1000)

        print("Stop connect attempts.")


    def attemptConnectToServer(self, address) -> None:
        self.recvSocket.bind(self.ownAddress)
        errno = self.recvSocket.connect_ex(address)

        if errno == 0 or errno == 10056:
            print("Connect success!")
            self.processConnectSuccess()


    def processConnectSuccess(self) -> None:
        self.recvSocket.setblocking(False)

        self.connected = True

        self.signalSetStateLabelNorm.emit(_('Norm'))


    def processConnectError(self, stateStrShort: str, stateStrFull='') -> None:
        self.connected = False

        if "Connect error" not in stateStrFull:
            super().addMsgToLogger('', stateStrFull + _(' in'))

        self.signalSetStateLabelError.emit(stateStrShort, stateStrFull)

        print("stateStrFull", stateStrFull)


    @pyqtSlot(str)
    def processToutAwaitingReceipt(self, msg: str) -> None:
        super().addMsgToLogger(msg, _('send failed (receipt timeout) from'))

        print("Restarting connection.")
        self.connected = False
