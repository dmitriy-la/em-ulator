import gettext

from PyQt5.Qt import Qt
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant

_ = gettext.gettext

COLUMN_INDEX_OF_MSG_TYPE_TITLE = 0
COLUMN_INDEX_OF_IF_MSG_TYPE_IS_RECEIPT = 1
COLUMN_INDEX_OF_IF_MSG_TYPE_SEND_ALLOWED = 2
COLUMN_INDEX_OF_HEX_FOR_MSG_TYPE = 3


class DataModelMsgTypes(QAbstractTableModel):
    def __init__(self, parent=None):
        super(DataModelMsgTypes, self).__init__(parent)
        self.columns = 3
        self.rows = 0
        self.msgTypesList = []
        self.msgTypesList.clear()


    def rowCount(self, parent) -> int:
        return self.rows


    def columnCount(self, parent) -> int:
        return self.columns


    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Vertical:
            return section

        if section == COLUMN_INDEX_OF_MSG_TYPE_TITLE:
            return _("Title")
        # if section == COLUMN_INDEX_OF_HEX_FOR_MSG_TYPE:
        #     return _("Hex for MSG type")
        if section == COLUMN_INDEX_OF_IF_MSG_TYPE_IS_RECEIPT:
            return _("Receipt")
        if section == COLUMN_INDEX_OF_IF_MSG_TYPE_SEND_ALLOWED:
            return _("Allow send")

        return QVariant()


    def appendMsgType(self, msgTypeDict: dict) -> None:
        self.beginInsertRows(QModelIndex(), self.rows, self.rows)
        self.msgTypesList.append(msgTypeDict)
        self.rows += 1
        self.endInsertRows()


    def insertColumn(self, column, parent):
        self.insertColumns(column, 1, parent)


    def insertColumns(self, column, count, parent):
        self.beginInsertColumns(QModelIndex(), column, (column + (count - 1)))
        self.endInsertColumns()


    def data(self, index, role) -> QVariant:
        if not index.isValid():
            return QVariant()

        elif self.gettingMsgTypeTitle(index, role):
            msgTypeDescr = self.msgTypesList[index.row()]
            return msgTypeDescr["msgTypeTitle"]

        # elif self.gettingHexForMsgType(index, role):
        #     msgTypeDescr = self.msgTypesList[index.row()]
        #     # print(msgTypeDescr)
        #     hexForMsgType = self.getHexForMsgType(msgTypeDescr)
        #     print("hexForMsgType", hexForMsgType)
        #     return hexForMsgType

        elif self.gettingIfMsgTypeIsReceipt(index, role):
            msgTypeDescr = self.msgTypesList[index.row()]
            return msgTypeDescr["isReceipt"]

        elif self.gettingIfMsgTypeSendAllowed(index, role):
            msgTypeDescr = self.msgTypesList[index.row()]
            return msgTypeDescr["sendAllowed"]

        else:
            return QVariant()


    def gettingMsgTypeTitle(self, index, role) -> bool:
        if index.column() == COLUMN_INDEX_OF_MSG_TYPE_TITLE and (role == Qt.DisplayRole or role == Qt.EditRole):
            return True
        else:
            return False


    def gettingHexForMsgType(self, index, role) -> bool:
        if index.column() == COLUMN_INDEX_OF_HEX_FOR_MSG_TYPE and role == Qt.DisplayRole:
            return True
        else:
            return False


    def getHexForMsgType(self, msgTypeDescr: dict) -> str:
        fieldDescrsList = msgTypeDescr["fieldDescrsList"]

        for fieldDescr in fieldDescrsList:
            if fieldDescr["fieldRole"] == "roleType":
                fieldValuesList = fieldDescr["fieldValuesList"]
                fieldValueDict = fieldValuesList[0]
                hexForMsgType = fieldValueDict["valueHex"]
                return hexForMsgType

        return ""


    def gettingIfMsgTypeIsReceipt(self, index, role) -> bool:
        if index.column() == COLUMN_INDEX_OF_IF_MSG_TYPE_IS_RECEIPT and role == Qt.DisplayRole:
            return True
        else:
            return False


    def gettingIfMsgTypeSendAllowed(self, index, role) -> bool:
        if index.column() == COLUMN_INDEX_OF_IF_MSG_TYPE_SEND_ALLOWED and role == Qt.DisplayRole:
            return True
        else:
            return False


    def setData(self, index, value, role=Qt.DisplayRole) -> bool:
        result = False

        if not index.isValid():
            result = False
        elif index.column() == COLUMN_INDEX_OF_MSG_TYPE_TITLE:
            result = self.setMsgTypeTitle(index, value)
        # elif index.column() == COLUMN_INDEX_OF_HEX_FOR_MSG_TYPE:
        #     result= self.setHexForMsgType(index, value)
        elif index.column() == COLUMN_INDEX_OF_IF_MSG_TYPE_IS_RECEIPT:
            result = self.setIfMsgTypeIsReceipt(index, value)
        elif index.column() == COLUMN_INDEX_OF_IF_MSG_TYPE_SEND_ALLOWED:
            result = self.setIfMsgTypeIsAllowed(index, value)

        return result


    def setHexForMsgType(self, index, value) -> bool:
        msgTypeDescr = self.msgTypesList[index.row()]
        fieldDescrsList = msgTypeDescr["fieldDescrsList"]

        result = False

        for fieldDescr in fieldDescrsList:
            if fieldDescr["fieldRole"] == "roleType":
                fieldValuesList = fieldDescr["fieldValuesList"]
                fieldValueDict = fieldValuesList[0]
                fieldValueDict["valueHex"] = value
                result = True

        return result


    def setIfMsgTypeIsAllowed(self, index, value) -> bool:
        msgTypeDescr = self.msgTypesList[index.row()]
        msgTypeDescr["sendAllowed"] = value
        result = value
        return result


    def setIfMsgTypeIsReceipt(self, index, value) -> bool:
        msgTypeDescr = self.msgTypesList[index.row()]
        msgTypeDescr["isReceipt"] = value
        result = value
        return result


    def setMsgTypeTitle(self, index, value) -> bool:
        allMsgTypeTitles = [msgTypeDescr["msgTypeTitle"] for msgTypeDescr in self.msgTypesList]
        allMsgTypeTitles.append(value)
        allUniqueMsgTypeTitles = set(allMsgTypeTitles)

        if len(allMsgTypeTitles) == len(allUniqueMsgTypeTitles):
            msgTypeDescr = self.msgTypesList.pop(index.row())
            msgTypeDescr["msgTypeTitle"] = value

            self.msgTypesList.insert(index.row(), msgTypeDescr)

            return True
        else:
            return False


    def flags(self, index) -> int:
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable


    def removeRows(self, startRow, count) -> None:
        self.beginRemoveRows(QModelIndex(), startRow, startRow + count - 1)

        for typeIter in self.msgTypesList:
            typeIter.pop()
        self.rows -= count

        self.endRemoveRows()
