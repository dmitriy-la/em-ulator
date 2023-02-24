import datetime
import gettext

from PyQt5.Qt import Qt
from PyQt5.QtCore import QPoint, QSize, QThread
from PyQt5.QtCore import pyqtBoundSignal, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAbstractItemView, QGroupBox, QHBoxLayout
from PyQt5.QtWidgets import QHeaderView, QLabel, QLayout
from PyQt5.QtWidgets import QPushButton, QTableView, QVBoxLayout


import src.datamodels.dataModelNamedMsg as dataModelNamedMsg
import src.handlers.handlerCrc as handlerCrc
import src.handlers.handlerMsgParse as handlerMsgParse
import src.handlers.handlerResponse as handlerResponse
import src.managers.managerDatalineSettings as managerDatalineSettings
import src.managers.managerNamedMsg as managerNamedMsg
import src.threads.threadTcpClient as threadTcpClient
import src.threads.threadTcpServer as threadTcpServer
import src.threads.threadUdp as threadUdp
import src.ui.windows.windowDatalineSettings as windowDatalineSettings
import src.ui.windows.windowNamedMsgEditor as windowNamedMsgEditor
import src.ui.windows.windowProfiledWindow as windowProfiledWindow


_ = gettext.gettext


class WindowDatalineWork(windowProfiledWindow.WindowProfiledWindow):
    signalToLoggerMsgReceived = pyqtSignal(str)
    signalToLoggerMsgSent = pyqtSignal(str)
    signalToLoggerMsgError = pyqtSignal(str)

    def __init__(self, profileTitle: str, datalineSettings: dict, parent=None):
        super().__init__(profileTitle, parent)
        self.datalineSettings = datalineSettings

        self.dataModelNamedMsgs = dataModelNamedMsg.DataModelNamedMsg(profileTitle)

        self.msgParser = handlerMsgParse.HandlerMsgParse(self.profileTitle)

        self.managerNamedMsg = managerNamedMsg.ManagerNamedMsg(self.profileTitle)

        self.responseHandler = handlerResponse.HandlerResponse(self.profileTitle)
        self.responseHandler.signalAddListOfMsgToSendingList.connect(self.addListOfMsgToSendingList)
        self.msgToBeSentList = self.responseHandler.getListOfMsgToSendAtStart()

        self.listClientThreads = []
        self.currentClientThread = 0

        self.sendMode = self.profileManager.getSendMode()

        self.running = True

        self.receiptOn = True
        self.initializingModeOn = True
        self.autofillId = True
        self.autofillCrc = True

        self.datalineSettingsWindowIsShown = False

        self.updateNamedMsgListForProfile()

        self.initUI()

        self.networkThread = self.startNetworkThread()


    def updateNamedMsgListForProfile(self) -> None:
        self.dataModelNamedMsgs.removeRows(0, self.dataModelNamedMsgs.rows)

        if len(self.dataModelNamedMsgs.namedMsgList) == 0:
            self.addAllNamedMsgToDataModel()


    def addAllNamedMsgToDataModel(self) -> None:
        allNamedMsgList = self.managerNamedMsg.getDataList()

        for namedMsgDict in allNamedMsgList:
            self.dataModelNamedMsgs.addNamedMsg(namedMsgDict)


    def initUI(self) -> None:
        self.setWindowProperties()

        self.principalLayout = QVBoxLayout(self)

        hLayWithState = self.getHLayWithState()
        self.principalLayout.addLayout(hLayWithState)

        msgManagementLayout = self.getMsgManagementLayout()
        self.principalLayout.addLayout(msgManagementLayout)

        self.buttonSave.hide()
        self.buttonClose.hide()

        self.oldPos = QPoint(self.x(), self.y())

        self.running = True

        self.show()


    def setWindowProperties(self) -> None:
        self.title = _(self.datalineSettings["title"])
        self.setWindowTitle(self.title)

        self.xCoord = 100
        self.yCoord = 100
        self.windowHeight = 200
        self.windowWidth = 320
        self.readSettings()

        self.setGeometry(self.xCoord, self.yCoord, self.windowWidth, self.windowHeight)

        flags = self.windowFlags()

        self.setWindowFlags(int(flags) | Qt.Tool)


    def readSettings(self) -> None:
        self.settings.beginGroup('/' + self.profileTitle)

        self.settings.beginGroup('/GraphicSettings' + self.title)
        try:
            self.xCoord = int(self.settings.value('/Left'))
            self.yCoord = int(self.settings.value('/Right'))
            self.windowHeight = int(self.settings.value('/Height'))
            self.windowWidth = int(self.settings.value('/Width'))
        except TypeError:
            self.xCoord = 10
            self.yCoord = 10
            self.windowHeight = 200
            self.windowWidth = 320

        self.settings.endGroup()
        self.settings.endGroup()


    def getHLayWithState(self) -> QLayout:
        hLayWithState = QHBoxLayout(self)
        self.addProtTypeLabel(hLayWithState)

        buttonRestart = self.getButtonRestart()
        hLayWithState.addWidget(buttonRestart)

        buttonStop = self.getButtonStop()
        buttonStop.clicked.connect(self.stopNetworkThread)
        hLayWithState.addWidget(buttonStop)

        self.labelNetStateCurrent = self.addLabelNetStateCurrent(hLayWithState)

        hLayWithState.addStretch(1)

        self.buttonShowSettings = self.addButtonShowSettings(hLayWithState)

        return hLayWithState


    def addProtTypeLabel(self, hLayWithState: QLayout) -> None:
        protType = self.datalineSettings["protocolType"]

        if protType == _("TCP-server"):
            protStr = "TCP-srv"
        elif protType == _("TCP-client"):
            protStr = "TCP-cli"
        elif protType == _("UDP"):
            protStr = "UDP"
        elif protType == _('raw'):
            protStr = "UDP-r"
        else:
            protStr = "UDP"

        labelProtocol = QLabel(protStr)
        labelProtocol.setToolTip(protType)
        hLayWithState.addWidget(labelProtocol)


    def getButtonRestart(self) -> QPushButton:
        buttonRestart = QPushButton(self)
        buttonRestart.setToolTip(_("Restart network thread"))
        buttonRestart.clicked.connect(self.restartNetworkThreadWithNewSettings)

        pixmap = QPixmap('../icons/play(1).png')
        playIcon = QIcon(pixmap)
        buttonRestart.setIcon(playIcon)
        buttonRestart.setIconSize(QSize(11, 11))

        return buttonRestart


    def getButtonStop(self) -> QPushButton:
        buttonStop = QPushButton(self)
        buttonStop.setToolTip(_("Stop network thread"))

        pixmap = QPixmap('../icons/stop(1).png')
        playIcon = QIcon(pixmap)
        buttonStop.setIcon(playIcon)
        buttonStop.setIconSize(QSize(11, 11))

        return buttonStop


    def addLabelNetStateCurrent(self, hLayWithState: QHBoxLayout) -> QLabel:
        labelNetStateCurrent = QLabel(self)

        labelNetStateCurrent.setText(_('Undef. state'))
        labelNetStateCurrent.setStyleSheet('QLabel {background-color : yellow; }')

        hLayWithState.addWidget(labelNetStateCurrent)

        return labelNetStateCurrent


    def addButtonShowSettings(self, hLayWithState: QLayout) -> QPushButton:
        buttonShowSettings = QPushButton()
        buttonShowSettings.setToolTip(_("Settings"))

        pixmap = QPixmap('../icons/settings.png')
        settingsIcon = QIcon(pixmap)
        buttonShowSettings.setIcon(settingsIcon)
        buttonShowSettings.setIconSize(QSize(15, 15))

        buttonShowSettings.clicked.connect(self.showDatalineSettigsWindow)

        hLayWithState.addWidget(buttonShowSettings)

        return buttonShowSettings


    def getMsgManagementLayout(self) -> QLayout:
        msgManagementLayout = QHBoxLayout(self)

        groupBoxWithListOfNamedMsgs = self.addGroupBoxWithListOfNamedMsgs(msgManagementLayout)

        layoutWithListOfNamedMsgs = QHBoxLayout(self)

        tableViewNamedMsgs = self.addTableViewNamedMsgs(groupBoxWithListOfNamedMsgs)
        self.selectionModelNamedMsgs = tableViewNamedMsgs.selectionModel()
        tableViewNamedMsgs.setSelectionModel(self.selectionModelNamedMsgs)
        layoutWithListOfNamedMsgs.addWidget(tableViewNamedMsgs)

        groupBoxWithListOfNamedMsgs.setLayout(layoutWithListOfNamedMsgs)

        layoutWithButtonsForMsgManagement = self.getButtonsLayout()
        layoutWithListOfNamedMsgs.addLayout(layoutWithButtonsForMsgManagement)
        msgManagementLayout.addLayout(layoutWithButtonsForMsgManagement)

        return msgManagementLayout


    def addGroupBoxWithListOfNamedMsgs(self, msgManagementLayout: QLayout) -> QGroupBox:
        groupBoxWithListOfNamedMsgs = QGroupBox(self)
        groupBoxWithListOfNamedMsgs.setTitle(_('List of created MSG'))
        groupBoxWithListOfNamedMsgs.setMinimumWidth(150)

        msgManagementLayout.addWidget(groupBoxWithListOfNamedMsgs)

        return groupBoxWithListOfNamedMsgs


    def addTableViewNamedMsgs(self, groupBoxWithListOfNamedMsgs: QGroupBox) -> QTableView:
        tableViewNamedMsgs = QTableView(groupBoxWithListOfNamedMsgs)

        self.dataModelNamedMsgs.dataChanged.connect(self.callResizeFunctionToResizeColumnWidth)

        tableViewNamedMsgs.setModel(self.dataModelNamedMsgs)
        tableViewNamedMsgs.setSelectionBehavior(QAbstractItemView.SelectRows)
        tableViewNamedMsgs.horizontalHeader().setStretchLastSection(True)

        tableViewNamedMsgs.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableViewNamedMsgs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        tableViewNamedMsgs.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        tableViewNamedMsgs.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        return tableViewNamedMsgs


    def callResizeFunctionToResizeColumnWidth(self) -> None:
        self.resize(self.size())


    def getButtonsLayout(self) -> QLayout:
        buttonsLay = QVBoxLayout(self)

        self.buttonSendNamedMsg = self.addButtonSendNamedMsg(buttonsLay)
        self.addButtonCreateNamedMsg(buttonsLay)
        self.addButtonRemoveNamedMsg(buttonsLay)
        buttonsLay.addStretch(1)

        return buttonsLay


    def addButtonSendNamedMsg(self, buttonsLay: QLayout) -> QPushButton:
        buttonSendNamedMsg = QPushButton()
        buttonSendNamedMsg.clicked.connect(self.sendNamedMsg)

        pixmap = QPixmap('../icons/paper-plane.png')
        saveIcon = QIcon(pixmap)
        buttonSendNamedMsg.setIcon(saveIcon)
        buttonSendNamedMsg.setIconSize(QSize(16, 16))

        buttonSendNamedMsg.setToolTip(_("Send selected message"))

        buttonsLay.addWidget(buttonSendNamedMsg)

        return buttonSendNamedMsg


    def addButtonCreateNamedMsg(self, buttonsLay: QLayout) -> None:
        buttonCreateNamedMsg = QPushButton()
        buttonCreateNamedMsg.clicked.connect(self.createNamedMsg)

        pixmap = QPixmap('../icons/add-document.png')
        saveIcon = QIcon(pixmap)
        buttonCreateNamedMsg.setIcon(saveIcon)
        buttonCreateNamedMsg.setIconSize(QSize(16, 16))

        buttonCreateNamedMsg.setToolTip("Create new named message")

        buttonsLay.addWidget(buttonCreateNamedMsg)


    def addButtonRemoveNamedMsg(self, buttonsLay: QLayout) -> None:
        buttonDelNamedMsg = QPushButton()
        buttonDelNamedMsg.clicked.connect(self.removeNamedMsg)

        pixmap = QPixmap('../icons/trash.png')
        saveIcon = QIcon(pixmap)
        buttonDelNamedMsg.setIcon(saveIcon)
        buttonDelNamedMsg.setIconSize(QSize(16, 16))

        buttonDelNamedMsg.setToolTip("Remove selected message from list")

        buttonsLay.addWidget(buttonDelNamedMsg)


    def startNetworkThread(self) -> QThread:
        self.labelNetStateCurrent.setText(_('UNDEF'))
        self.labelNetStateCurrent.setStyleSheet('QLabel {background-color : yellow; }')

        if self.datalineSettings["protocolType"] == 'TCP-server':
            self.networkThread = threadTcpServer.ThreadTcpServer(self.datalineSettings, self)
            print('Started TCP-server.')
        elif self.datalineSettings["protocolType"] == 'TCP-client':
            self.networkThread = threadTcpClient.ThreadTcpClient(self.datalineSettings, self)
            print('Started TCP-client.')
        elif self.datalineSettings["protocolType"] == 'UDP':
            self.networkThread = threadUdp.ThreadUdp(self.datalineSettings, self)
            print('Started UDP.')
        elif self.datalineSettings["protocolType"] == 'raw':
            self.networkThread = threadUdp.ThreadUdp(self.datalineSettings, self)
            print('Started UDP-raw.')
        else:
            self.networkThread = threadUdp.ThreadUdp(self.datalineSettings, self)
            print('Started UDP.')

        self.networkThread.signalSetStateLabelNorm.connect(self.setStateLabelNorm)
        self.networkThread.signalSetStateLabelError.connect(self.setStateLabelError)

        self.networkThread.start()

        return self.networkThread


    @pyqtSlot(str)
    def setStateLabelNorm(self, stateStrShort=_('Norm')) -> None:
        self.labelNetStateCurrent.setText(stateStrShort)
        self.labelNetStateCurrent.setStyleSheet('QLabel {background-color : limegreen; }')


    @pyqtSlot(str, str)
    def setStateLabelError(self, stateStrShort: str, stateStrFull: str) -> None:
        self.labelNetStateCurrent.setText(stateStrShort)
        self.labelNetStateCurrent.setToolTip(stateStrFull)
        self.labelNetStateCurrent.setStyleSheet('QLabel {background-color : red; }')


    @pyqtSlot()
    def showDatalineSettigsWindow(self) -> None:
        if not self.datalineSettingsWindowIsShown:
            datalineSettingsEditor = windowDatalineSettings.WindowDatalineSettings(self.profileTitle, self)
            datalineSettingsEditor.exec_()
            self.datalineSettingsWindowIsShown = True


    @pyqtSlot()
    def sendNamedMsg(self) -> None:
        # print("sending named msg")
        indexes = self.selectionModelNamedMsgs.selectedIndexes()

        listOfMsgToSend = []
        for index in indexes:
            if index.column() == 1:
                msgToSend = index.data()
                listOfMsgToSend.append(msgToSend)

        self.addListOfMsgToSendingList(listOfMsgToSend)


    def sendingMessagesSequentally(self) -> bool:
        if self.sendMode != 'parallel':
            return True
        else:
            return False


    @pyqtSlot(str)
    def resendMsg(self, msgToSend: str) -> None:
        self.msgToBeSentList.append(msgToSend)


    @pyqtSlot(list)
    def addListOfMsgToSendingList(self, listOfMsgToSend: list) -> None:
        for msgToSend in listOfMsgToSend:
            self.addMsgToSendingList(msgToSend)


    @pyqtSlot(str)
    def addMsgToSendingList(self, msgToSend: str) -> None:
        if msgToSend != '':
            msgToSend = self.autofillIdAndCrcIfNeeded(msgToSend)
            msgToSend = msgToSend.replace('x', '0')
            msgToSend = msgToSend.strip()

            if self.datalineSettings["protocolType"] == "TCP-server":
                listOfClientThreadsToSendMsgTo = self.getListOfClientThreadsToSendMsgTo()

                if len(listOfClientThreadsToSendMsgTo) == 0:
                    self.addMsgToLogger(msgToSend, _("No clients to send to from"))
                else:
                    for clientThread in listOfClientThreadsToSendMsgTo:
                        clientThread.addMsgToBeSent(msgToSend)
            else:
                self.msgToBeSentList.append(msgToSend)


    def autofillIdAndCrcIfNeeded(self, msgToSend: str) -> str:
        if self.autofillId:
            msgToSend = self.responseHandler.setIdInOutgoingMsg(msgToSend)
            print("After id", msgToSend)
        if self.autofillCrc:
            crcHandler = handlerCrc.HandlerCrc(self.profileTitle)
            msgToSend = crcHandler.getMsgWithCrc(msgToSend)
            print("After crc", msgToSend)

        return msgToSend


    def getListOfClientThreadsToSendMsgTo(self) -> list:
        if self.consecutiveSendingToClients() and self.thereAreConnectedClients():
            return [self.listClientThreads[self.currentClientThread]]
        else:
            return self.listClientThreads


    def sendMsgToEveryClient(self, msgToSend) -> None:
        for clientThread in self.listClientThreads:
            clientThread.addMsgToBeSent(msgToSend)


    def thereAreConnectedClients(self) -> bool:
        if len(self.listClientThreads) > 0:
            return True
        else:
            return False


    def consecutiveSendingToClients(self) -> bool:
        sendMode = self.datalineSettings["sendMode"]
        if sendMode == _("send to one client, switch between clients on tout"):
            return True
        else:
            return False


    @pyqtSlot(str)
    def addToutAwaitingReceiptToLogger(self, msg: str) -> None:
        self.addMsgToLogger(msg, _("receipt timeout for msg to"))


    @pyqtSlot()
    def createNamedMsg(self) -> None:
        namedMsgEditor = windowNamedMsgEditor.WindowNamedMsgEditor(self.profileTitle)
        namedMsgEditor.signalNamedMsgAdded.connect(self.addNamedMsgToDataModel)
        namedMsgEditor.exec_()


    @pyqtSlot(dict)
    def addNamedMsgToDataModel(self, namedMsgDict: dict) -> None:
        self.dataModelNamedMsgs.addNamedMsg(namedMsgDict)


    @pyqtSlot()
    def removeNamedMsg(self) -> None:
        indexes = self.selectionModelNamedMsgs.selectedIndexes()

        if len(indexes) <= 0:
            return

        for index in indexes:
            if index.column() == 0:
                self.managerNamedMsg.removeNamedMsg(index.data())

        firstRowToRemove = indexes[0].row()
        lastRowToRemove = indexes[len(indexes) - 1].row()
        rowsCountToRemove = lastRowToRemove - firstRowToRemove + 1
        self.dataModelNamedMsgs.removeRows(firstRowToRemove, rowsCountToRemove)


    @pyqtSlot()
    def restartNetworkThreadWithNewSettings(self) -> None:
        self.stopNetworkThread()

        self.running = True

        self.networkThread = self.startNetworkThread()


    @pyqtSlot()
    def stopNetworkThread(self) -> None:
        print("Stopping network thread.")
        self.msgToBeSentList.clear()
        self.labelNetStateCurrent.setText(_('STOP'))
        self.labelNetStateCurrent.setStyleSheet('QLabel {background-color : red; }')

        self.running = False
        if self.networkThread is not None:
            self.networkThread.closeSockets()
            self.networkThread.wait()


    def updateDatalineSettings(self) -> None:
        datalineManager = managerDatalineSettings.ManagerDatalineSettings(self.profileTitle)
        datalineTitle = self.datalineSettings["title"]
        self.datalineSettings = datalineManager.getDatalineSettingsByDatalineTitle(datalineTitle)

        if self.datalineSettings["protocolType"] == 'TCP-server':
            self.updateReceiptingSettingsForEachClientThread()
        else:
            self.networkThread.updateReceiptingSettings()


    def updateReceiptingSettingsForEachClientThread(self) -> None:
        for clientThread in self.listClientThreads:
            clientThread.updateReceiptingSettings()


    def addMsgToLogger(self, msg: str, stringComment='') -> None:
        strTime = self.getStrTime()

        msgStr = self.getPreparedMsgStr(msg)

        if _('received') in stringComment:
            msgStr = self.msgParser.getMsgWithSpacesFromReceivedNsg(msgStr)

        msgStr = ' '.join(msgStr.split())

        datalineTitleStr = " {}".format(self.title)
        indentStr = ":\n             "
        loggerMsg = strTime + ', ' \
                            + stringComment \
                            + datalineTitleStr \
                            + indentStr \
                            + msgStr

        parsingNecessary = (msgStr != '' and (_('sent') in stringComment or _('received') in stringComment))

        if parsingNecessary:
            loggerMsg = loggerMsg + self.msgParser.getParsedMsgStrFromMsg(msgStr)
        else:
            loggerMsg = loggerMsg.replace(':', '.')

        loggerMsg = loggerMsg.strip(indentStr)

        signal = self.getSignalToLoggerFromStringComment(stringComment)

        signal.emit(loggerMsg)


    def getStrTime(self) -> str:
        time = datetime.datetime.now().time()
        strTime = time.strftime('%H:%M:%S.%f')
        strTime = strTime[:-4]

        return strTime


    def getPreparedMsgStr(self, msg) -> str:
        if type(msg) == bytes or type(msg) == bytearray:
            msgStr = msg.decode('utf-8', 'replace')
        else:
            msgStr = str(msg)

        msgStr = msgStr.replace("b\'", "")
        msgStr = msgStr.replace('\\x', "")
        msgStr = msgStr.replace("\'", "")

        return msgStr


    def getSignalToLoggerFromStringComment(self, stringComment: str) -> pyqtBoundSignal:
        if _('sent') in stringComment:
            signal = self.signalToLoggerMsgSent
        elif _('received') in stringComment:
            signal = self.signalToLoggerMsgReceived
        else:
            signal = self.signalToLoggerMsgError

        return signal


    def mousePressEvent(self, event) -> None:
        self.oldPos = event.globalPos()


    def mouseMoveEvent(self, event) -> None:
        delta = QPoint(event.globalPos() - self.oldPos)

        self.move(self.x() + delta.x(), self.y() + delta.y())

        self.oldPos = event.globalPos()


    def closeEvent(self, event) -> None:
        print("Closing dataline", self.title)

        self.running = False

        if self.networkThread is not None:
            self.networkThread.closeSockets()
            self.networkThread.wait()

        namedMsgList = self.dataModelNamedMsgs.namedMsgList
        self.managerNamedMsg.updateDataFile(namedMsgList)

        self.writeSettings()

        self.close()


    def writeSettings(self) -> None:
        self.settings.beginGroup('/' + self.profileTitle)

        self.settings.beginGroup('/GraphicSettings' + self.title)
        self.settings.setValue('/Left', int(self.x()))
        self.settings.setValue('/Right', int(self.y()))
        self.settings.setValue('/Height', int(self.height()))
        self.settings.setValue('/Width', int(self.width()))
        self.settings.endGroup()

        self.settings.endGroup()
