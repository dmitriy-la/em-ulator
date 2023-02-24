import gettext
import socket

from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal

import src.threads.threadForSingleTcpClientInTcpServer as threadForSingleTcpClientInTcpServer


_ = gettext.gettext


class ThreadTcpServer(QThread):
    signalSetStateLabelNorm = pyqtSignal(str)
    signalSetStateLabelError = pyqtSignal(str, str)

    def __init__(self, datalineSettings: dict, parent=None):
        """
        Multithreaded Python server - TCP Server Socket Thread Pool
        :param datalineSettings:
        :param parent:
        """
        QThread.__init__(self)
        self.parent = parent
        self.datalineSettings = datalineSettings

        self.serverOwnAddress = (datalineSettings["ipOwn"], datalineSettings["portOwn"])
        self.serverSendAddress = (datalineSettings["ipSend"], datalineSettings["portSend"])

        self.tcpServerSocketRecv = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.tcpServerSocketRecv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print('Started TCP-server.')


    def run(self):
        self.openSocket()
        print('TCP-server', self.serverOwnAddress)

        while self.parent.running:
            if self.noClientsConnectedToServerAndTryingToSend():
                self.proccessNoClientsWhenTryingToSend()
            try:
                clientSocket, ip, port = self.getIncomingConnection()

                self.startThreadForConnectedTcpClient(clientSocket, ip, port)
            except BlockingIOError:
                continue
            except OSError:
                self.closeSockets()

                self.parent.msgToBeSentList.clear()

                self.signalSetStateLabelError.emit(_('STOP'), '')
                break

            self.msleep(100)

        print('TCP-server main thread stopped.')


    def openSocket(self) -> None:
        try:
            self.tcpServerSocketRecv.setblocking(False)

            self.tcpServerSocketRecv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.tcpServerSocketRecv.bind(self.serverOwnAddress)

            self.signalSetStateLabelNorm.emit(_('Norm, no clients'))
        except OSError:
            self.closeSockets()
            self.parent.msgToBeSentList.clear()

            self.signalSetStateLabelError.emit(_('STOP: Address already in use'), '')


    def closeSockets(self) -> None:
        self.tcpServerSocketRecv.close()

        for clientThread in self.parent.listClientThreads:
            clientThread.stopThreadForSingleClient()
            clientThread.wait()

        print("All client threads closed.")

        self.parent.listClientThreads.clear()


    def noClientsConnectedToServerAndTryingToSend(self) -> bool:
        if len(self.parent.listClientThreads) == 0 and len(self.parent.msgToBeSentList) > 0:
            return True
        else:
            return False


    def proccessNoClientsWhenTryingToSend(self) -> None:
        for msg in self.parent.msgToBeSentList:
            self.parent.addMsgToLogger(msg, _('error - no clients'))

        self.parent.msgToBeSentList.clear()


    def getIncomingConnection(self) -> tuple:
        self.tcpServerSocketRecv.listen(4)

        (clientSocket, (ip, port)) = self.tcpServerSocketRecv.accept()
        clientSocket.setblocking(False)
        clientSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        return clientSocket, ip, port


    def startThreadForConnectedTcpClient(self, clientSocket, ip, port) -> None:
        threadIndex = self.getIndexForNewThread()

        self.stopThreadForClientIfNeeded(ip, port)

        newClientThreadSettings = self.datalineSettings.copy()
        newClientThreadSettings["ipOwn"] = ip
        newClientThreadSettings["portOwn"] = port

        clientThreadArgs = [newClientThreadSettings, clientSocket, threadIndex, self.parent]
        newthread = threadForSingleTcpClientInTcpServer.ThreadForSingleTcpClientInTcpServer(*clientThreadArgs)

        self.parent.listClientThreads.append(newthread)
        newthread.start()

        clientThreadsCount = len(self.parent.listClientThreads)
        strClientThreadsCount = str(clientThreadsCount)

        self.signalSetStateLabelNorm.emit(_('Norm, clients: ') + strClientThreadsCount)


    def getIndexForNewThread(self) -> int:
        return len(self.parent.listClientThreads)


    def stopThreadForClientIfNeeded(self, ip, port) -> None:
        for clientThread in self.parent.listClientThreads:
            if clientThread.ip == ip and clientThread.port == port:
                clientThread.stopThreadForSingleClient()
                clientThread.wait()
                print("Thread for previously connected client:", ip, port, "has been stopped.")
