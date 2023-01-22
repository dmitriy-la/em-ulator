import gettext
import ipaddress
import socket

from PyQt5.Qt import Qt
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant

_ = gettext.gettext

ROW_INDEX_OF_DATALINE_TITLE = 0
ROW_INDEX_OF_DATALINE_PROTOCOL = 1
ROW_INDEX_OF_DATALINE_IP_OWN = 2
ROW_INDEX_OF_DATALINE_PORT_OWN = 3
ROW_INDEX_OF_DATALINE_IP_SEND = 4
ROW_INDEX_OF_DATALINE_PORT_SEND = 5
ROW_INDEX_OF_DATALINE_TOUT = 6
ROW_INDEX_OF_DATALINE_REPEATS = 7
ROW_INDEX_OF_DATALINE_RECEIPT_DELAY = 8
ROW_INDEX_OF_DATALINE_SEND_MODE = 9


class DataModelDataline(QAbstractTableModel):
    def __init__(self, parent=None):
        super(DataModelDataline, self).__init__(parent)
        self.rows = 0
        self.datalineList = []


    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Vertical:
            return section

        if section == ROW_INDEX_OF_DATALINE_TITLE:
            return _("Title")

        elif section == ROW_INDEX_OF_DATALINE_PROTOCOL:
            return _("Protocol")

        elif section == ROW_INDEX_OF_DATALINE_IP_OWN:
            return _("IP own")

        elif section == ROW_INDEX_OF_DATALINE_PORT_OWN:
            return _("Port own")

        elif section == ROW_INDEX_OF_DATALINE_IP_SEND:
            return _("IP send")

        elif section == ROW_INDEX_OF_DATALINE_PORT_SEND:
            return _("Port send")

        elif section == ROW_INDEX_OF_DATALINE_TOUT:
            return _("Tout, ms")

        elif section == ROW_INDEX_OF_DATALINE_REPEATS:
            return _("Reps")

        elif section == ROW_INDEX_OF_DATALINE_RECEIPT_DELAY:
            return _("Receipt delay")

        elif section == ROW_INDEX_OF_DATALINE_SEND_MODE:
            return _("Send mode")

        else:
            return QVariant()


    def data(self, index, role) -> QVariant:
        datalineIndex = index.row()
        currentDatalineDict = self.datalineList[datalineIndex]

        if self.dataIsNotRetrievable(index, role):
            return QVariant()
        elif self.gettingDatalineTitle(index):
            return currentDatalineDict['title']
        elif self.gettingDatalineProtocol(index):
            return currentDatalineDict['protocolType']
        elif self.gettingDatalineIpOwn(index):
            return currentDatalineDict['ipOwn']
        elif self.gettingDatalinePortOwn(index):
            return currentDatalineDict['portOwn']
        elif self.gettingDatalineIpSend(index):
            return currentDatalineDict['ipSend']
        elif self.gettingDatalinePortSend(index):
            return currentDatalineDict['portSend']
        elif self.gettingDatalineTimeoutMs(index):
            return currentDatalineDict['toutMs']
        elif self.gettingDatalineRepeats(index):
            return currentDatalineDict['repeats']
        elif self.gettingDatalineReceiptDelay(index):
            return currentDatalineDict['delay']
        elif self.gettingDatalineSendMode(index):
            return self.getSendMode(index)

        return QVariant()


    def dataIsNotRetrievable(self, index, role) -> bool:
        if not index.isValid() or (role != Qt.DisplayRole and role != Qt.EditRole):
            return True
        elif self.datalineList.__len__() == 0:
            return True

        return False


    def gettingDatalineTitle(self, index) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_TITLE:
            return True
        return False


    def gettingDatalineProtocol(self, index) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_PROTOCOL:
            return True
        return False


    def gettingDatalineIpOwn(self, index) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_IP_OWN:
            return True
        return False


    def gettingDatalinePortOwn(self, index) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_PORT_OWN:
            return True
        return False


    def gettingDatalineIpSend(self, index) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_IP_SEND:
            return True
        return False


    def gettingDatalinePortSend(self, index) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_PORT_SEND:
            return True
        return False


    def gettingDatalineTimeoutMs(self, index) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_TOUT:
            return True
        return False


    def gettingDatalineRepeats(self, index) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_REPEATS:
            return True
        return False


    def gettingDatalineReceiptDelay(self, index) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_RECEIPT_DELAY:
            return True
        return False


    def gettingDatalineSendMode(self, index) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_SEND_MODE:
            return True
        return False


    def getSendMode(self, index) -> QVariant:
        datalineIndex = index.row()
        currentDatalineDict = self.datalineList[datalineIndex]

        if currentDatalineDict['protocolType'] == "TCP-server":
            return currentDatalineDict['sendMode']
        else:
            return QVariant()


    def setData(self, index, value, role) -> bool:
        setDataResult = False

        if self.unableToSetData(index, value):
            setDataResult = False

        elif self.editingDatalineTitle(index, role):
            setDataResult = self.setNewTitleForDataline(index, value)

        elif self.editingDatalineProtocol(index):
            setDataResult = self.setNewProtocolForDataline(index, value)

        elif self.editingDatalineIpOwn(index, role):
            setDataResult = self.setNewIpOwnForDataline(index, value)

        elif self.editingDatalinePortOwn(index, role):
            setDataResult = self.setNewPortOwnForDataline(index, value)

        elif self.editingDatalineIpSend(index, role):
            setDataResult = self.setNewIpSendDataline(index, value)

        elif self.editingDatalinePortSend(index, role):
            setDataResult = self.setNewPortSendDataline(index, value)

        elif self.editingDatalineTimeout(index, role):
            setDataResult = self.setNewToutForDataline(index, value)

        elif self.editingDatalineRepeats(index, role):
            setDataResult = self.setNewRepeatsForDataline(index, value)

        elif self.editingDatalineReceiptDelay(index, role):
            setDataResult = self.setNewReceiptDelayForDataline(index, value)

        elif self.editingDatalineSendMode(index):
            setDataResult = self.setNewSendModeForDataline(index, value)
        else:
            setDataResult = False

        return setDataResult


    def unableToSetData(self, index, value) -> bool:
        if not index.isValid() or value == '':
            return True


    def editingDatalineTitle(self, index, role) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_TITLE and role == Qt.EditRole:
            return True
        else:
            return False


    def setNewTitleForDataline(self, index, value) -> bool:
        if self.titleIsUnique(value):
            datalineData = self.datalineList[index.row()]
            datalineData['title'] = value
            result = True
        else:
            result = False
        return result


    def titleIsUnique(self, value) -> bool:
        allDatalineTitlesList = [dataline['title'] for dataline in self.datalineList]

        if value in allDatalineTitlesList:
            print('Not unique!')
            return False
        else:
            return True


    def editingDatalineProtocol(self, index) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_PROTOCOL:
            return True
        else:
            return False


    def setNewProtocolForDataline(self, index, value) -> bool:
        currentDatalineDescr = self.datalineList[index.row()]
        currentDatalineDescr['protocolType'] = value
        result = True
        return result


    def editingDatalineIpOwn(self, index, role) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_IP_OWN and role == Qt.EditRole:
            return True
        else:
            return False


    def setNewIpOwnForDataline(self, index, value) -> bool:
        datalineData = self.datalineList[index.row()]

        if self.isValidIpAddressV4(value) or self.isValidIpAddressV6(value):
            datalineData['ipOwn'] = value
            result = True
        else:
            result = False

        return result


    def editingDatalinePortOwn(self, index, role) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_PORT_OWN and role == Qt.EditRole:
            return True
        else:
            return False


    def setNewPortOwnForDataline(self, index, value) -> bool:
        datalineData = self.datalineList[index.row()]
        datalineData['portOwn'] = value
        result = True
        return result


    def editingDatalineIpSend(self, index, role) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_IP_SEND and role == Qt.EditRole:
            return True
        else:
            return False


    def setNewIpSendDataline(self, index, value) -> bool:
        if self.isValidIpAddressV4(value) or self.isValidIpAddressV6(value):
            datalineData = self.datalineList[index.row()]
            datalineData['ipSend'] = value
            result = True
        else:
            result = False
        return result


    def editingDatalinePortSend(self, index, role) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_PORT_SEND and role == Qt.EditRole:
            return True
        else:
            return False


    def setNewPortSendDataline(self, index, value) -> bool:
        datalineData = self.datalineList[index.row()]
        datalineData['portSend'] = value
        result = True
        return result


    def editingDatalineTimeout(self, index, role) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_TOUT and role == Qt.EditRole:
            return True
        else:
            return False


    def setNewToutForDataline(self, index, value) -> bool:
        datalineData = self.datalineList[index.row()]
        datalineData['toutMs'] = value
        result = True
        return result


    def editingDatalineRepeats(self, index, role) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_REPEATS and role == Qt.EditRole:
            return True
        else:
            return False


    def setNewRepeatsForDataline(self, index, value) -> bool:
        datalineData = self.datalineList[index.row()]
        datalineData['repeats'] = value
        result = True
        return result


    def editingDatalineReceiptDelay(self, index, role) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_RECEIPT_DELAY and role == Qt.EditRole:
            return True
        else:
            return False


    def setNewReceiptDelayForDataline(self, index, value) -> bool:
        datalineData = self.datalineList[index.row()]
        datalineData['delay'] = value
        result = True
        return result


    def editingDatalineSendMode(self, index) -> bool:
        if index.column() == ROW_INDEX_OF_DATALINE_SEND_MODE:
            return True
        else:
            return False


    def setNewSendModeForDataline(self, index, value) -> bool:
        datalineData = self.datalineList[index.row()]
        datalineData['sendMode'] = value
        result = True
        return result


    def appendDatalineRow(self, datalineDict: dict) -> None:
        self.rows += 1

        self.beginInsertRows(QModelIndex(), self.rows, self.rows)

        title = datalineDict["title"]
        if title == 'default':
            title += ' ' + str(self.rows)

        self.datalineList.append(datalineDict)

        self.endInsertRows()


    def flags(self, index):
        flags = QAbstractTableModel.flags(self, index)

        if index.isValid():
            flags = self.getFlags(index)

        return flags


    def getFlags(self, index):
        flags = QAbstractTableModel.flags(self, index)
        currentDataline = self.datalineList[index.row()]
        currentDatalineProtocol = currentDataline['protocolType']

        if index.column() == 9 and currentDatalineProtocol != "TCP-server":
            return int(flags) & ~Qt.ItemIsEnabled
        else:
            return int(flags) | Qt.ItemIsEditable


    def insertRow(self, row, parent) -> bool:
        self.rows += 1
        return self.insertRows(row, 1, parent)


    def insertRows(self, row, count, parent) -> bool:
        self.beginInsertRows(QModelIndex(), row, row + count - 1)
        self.endInsertRows()
        return True


    def removeRows(self, startRow, count) -> None:
        self.beginRemoveRows(QModelIndex(), startRow, startRow + count - 1)

        for datalineIndex in range(startRow + count-1, startRow-1, -1):
            datalineDescrToRemove = self.datalineList[datalineIndex]
            self.datalineList.remove(datalineDescrToRemove)
        self.rows -= count

        self.endRemoveRows()


    def rowCount(self, parent) -> int:
        return self.rows


    def columnCount(self, parent) -> int:
        return 10


    def isValidIpAddressV4(self, address) -> bool:
        try:
            ipaddress.ip_address(address)
            return True
        except ValueError:
            print('address/netmask is invalid:', address)
            return False


    def isValidIpAddressV6(self, address) -> bool:
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:
            print("Invalid address")
            return False

        return True
