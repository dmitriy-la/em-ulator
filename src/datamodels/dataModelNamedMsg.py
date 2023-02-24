import gettext

from PyQt5.Qt import Qt
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant

import src.handlers.handlerMsgParse as handlerMsgParse
import src.managers.managerNamedMsg as managerNamedMsg

_ = gettext.gettext


COLUMN_INDEX_OF_NAMED_MSG_TITLE = 0
COLUMN_INDEX_OF_NAMED_MSG_HEX = 1


class DataModelNamedMsg(QAbstractTableModel):
    def __init__(self, profileTitle: str, parent=None):
        super(DataModelNamedMsg, self).__init__(parent)
        self.rows = 0
        self.namedMsgList = []

        self.managerNamedMsg = managerNamedMsg.ManagerNamedMsg(profileTitle)
        self.parser = handlerMsgParse.HandlerMsgParse(profileTitle)


    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Vertical:
            return section

        if section == COLUMN_INDEX_OF_NAMED_MSG_TITLE:
            return _("Title")
        if section == COLUMN_INDEX_OF_NAMED_MSG_HEX:
            return _("Message")

        return QVariant()


    def data(self, index, role):
        if self.dataIsNotRetrievable(index, role):
            return QVariant()

        elif self.gettingMsgTitle(index, role):
            msgTitle = self.getMsgTitle(index)
            return msgTitle

        elif self.gettingMsgHex(index, role):
            msgHex = self.getMsgHex(index)
            return msgHex

        return QVariant()


    def dataIsNotRetrievable(self, index, role) -> bool:
        if not index.isValid() or (role != Qt.DisplayRole and role != Qt.EditRole):
            return True
        elif self.namedMsgList.__len__() == 0 or index.row() >= self.namedMsgList.__len__():
            return True

        return False


    def gettingMsgTitle(self, index, role) -> bool:
        if index.column() == COLUMN_INDEX_OF_NAMED_MSG_TITLE and (role == Qt.DisplayRole or role == Qt.EditRole):
            return True
        else:
            return False


    def gettingMsgHex(self, index, role) -> bool:
        if index.column() == COLUMN_INDEX_OF_NAMED_MSG_HEX and (role == Qt.DisplayRole or role == Qt.EditRole):
            return True
        else:
            return False


    def getMsgHex(self, index) -> str:
        msgIndex = index.row()
        namedMsg = self.namedMsgList[msgIndex]
        msgHex = namedMsg["msgHex"].strip()
        return msgHex


    def getMsgTitle(self, index) -> str:
        msgIndex = index.row()
        namedMsg = self.namedMsgList[msgIndex]
        msgTitle = namedMsg["msgTitle"].strip()
        return msgTitle


    def setData(self, index, value, role) -> bool:
        setResult = False

        if not index.isValid():
            return False
        elif self.editingNamedMsgTitle(index, role):
            setResult = self.setNewMsgTitle(index, value)
        elif self.editingNamedMsgHex(index, role):
            setResult = self.setNewMsgHex(index, value)

        if setResult is True:
            # For resizing column's width:
            self.dataChanged.emit(QModelIndex(), QModelIndex())
            # Saving changes
            namedMsgList = self.namedMsgList
            self.managerNamedMsg.updateNamedMsgListFile(namedMsgList)

        return setResult


    def editingNamedMsgTitle(self, index, role) -> bool:
        if index.column() == COLUMN_INDEX_OF_NAMED_MSG_TITLE and role == Qt.EditRole:
            return True
        else:
            return False


    def setNewMsgTitle(self, index, value) -> bool:
        if self.enteredNamedMsgTitleIsUnique(value):
            field = self.namedMsgList[index.row()]
            field["msgTitle"] = value
            return True
        else:
            return False


    def enteredNamedMsgTitleIsUnique(self, msgTitle: str) -> bool:
        allNamedMsgTitlesList = [namedMsg["msgTitle"] for namedMsg in self.namedMsgList]

        if msgTitle in allNamedMsgTitlesList:
            print('Not unique!')
            return False
        else:
            return True


    def editingNamedMsgHex(self, index, role) -> bool:
        if index.column() == COLUMN_INDEX_OF_NAMED_MSG_HEX and role == Qt.EditRole:
            return True
        else:
            return False


    def setNewMsgHex(self, index, value) -> bool:
        value = value.replace('x', '0')

        if self.enteredHexMsgIsValid(value):
            field = self.namedMsgList[index.row()]
            field["msgHex"] = value
            return True
        else:
            return False


    def enteredHexMsgIsValid(self, msg: str) -> bool:
        return False


    def addNamedMsg(self, namedMsgDict: dict) -> None:
        self.rows += 1

        self.beginInsertRows(QModelIndex(), self.rows, self.rows)
        self.namedMsgList.append(namedMsgDict)

        self.endInsertRows()


    def flags(self, index):
        flags = QAbstractTableModel.flags(self, index)
        if index.isValid():
            if index.column() == 0:
                return flags | Qt.ItemIsEditable
            else:
                return flags
        else:
            return flags


    def insertColumn(self, parent) -> None:
        self.insertColumns(1, 1, parent)


    def rowCount(self, parent) -> int:
        return self.rows


    def columnCount(self, parent) -> int:
        return 2


    def insertColumns(self, column, count, parent) -> None:
        self.beginInsertColumns(QModelIndex(), column, (column + (count - 1)))
        self.endInsertColumns()


    def insertRow(self, row, parent) -> bool:
        self.rows += 1
        return self.insertRows(row, 1, parent)


    def insertRows(self, row, count, parent) -> bool:
        self.beginInsertRows(QModelIndex(), row, row + count - 1)
        self.endInsertRows()
        return True


    def removeRows(self, startRow, count) -> None:
        self.beginRemoveRows(QModelIndex(), startRow, startRow + count - 1)

        for i in range(startRow + count-1, startRow-1, -1):
            self.namedMsgList.remove(self.namedMsgList[i])

        self.rows -= count
        self.endRemoveRows()
