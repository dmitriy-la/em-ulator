import gettext

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant
from PyQt5.Qt import Qt

_ = gettext.gettext


COLUMN_INDEX_OF_VALUE_HEX = 0
COLUMN_INDEX_OF_VALUE_MEANING = 1


class DataModelValues(QAbstractTableModel):
    def __init__(self, parent=None):
        super(DataModelValues, self).__init__(parent)
        self.rows = 0

        self.valuesList = []
        self.valuesList.clear()


    def rowCount(self, parent) -> int:
        return self.rows


    def columnCount(self, parent) -> int:
        return 2


    def headerData(self, section, orientation, role) -> QVariant:
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Vertical:
            return section

        if section == COLUMN_INDEX_OF_VALUE_HEX:
            return _("Value hex")
        if section == COLUMN_INDEX_OF_VALUE_MEANING:
            return _("Value meaning")

        return QVariant()


    def appendValueRow(self, value, meaning) -> None:
        self.rows += 1

        self.beginInsertRows(QModelIndex(), self.rows, self.rows)
        fieldDescr = {"valueHex": value, "valueMeaning": meaning}
        self.valuesList.append(fieldDescr)

        self.endInsertRows()


    def data(self, index, role) -> QVariant:
        if self.dataIsNotRetrievable(index, role):
            return QVariant()

        elif self.gettingValueHex(index, role):
            valueHex = self.getValueHex(index)
            return valueHex

        elif self.gettingValueMeaning(index, role):
            valueMeaning = self.getValueMeaning(index)
            return valueMeaning

        else:
            return QVariant()


    def dataIsNotRetrievable(self, index, role) -> bool:
        if not index.isValid() or (role != Qt.DisplayRole and role != Qt.EditRole):
            return True
        elif self.valuesList.__len__() == 0:
            return True

        return False


    def gettingValueHex(self, index, role) -> bool:
        if index.column() == COLUMN_INDEX_OF_VALUE_HEX and role == Qt.DisplayRole:
            return True
        else:
            return False


    def getValueHex(self, index) -> str:
        valueDict = self.valuesList[index.row()]
        valueHex = valueDict["valueHex"]
        return valueHex


    def gettingValueMeaning(self, index, role) -> bool:
        if index.column() == COLUMN_INDEX_OF_VALUE_MEANING and role == Qt.DisplayRole:
            return True
        else:
            return False


    def getValueMeaning(self, index) -> str:
        valueDict = self.valuesList[index.row()]
        valueMeaning = valueDict["valueMeaning"]
        return valueMeaning


    def setData(self, index, value, role) -> bool:
        setDataResult = False

        if not index.isValid():
            return False
        elif self.editingValueHex(index, role):
            setDataResult = self.setValueHex(index, value)
        elif index.column() == COLUMN_INDEX_OF_VALUE_MEANING and role == Qt.EditRole:
            valueRow = self.valuesList[index.row()]
            valueRow["valueMeaning"] = value

        return setDataResult


    def editingValueHex(self, index, role) -> bool:
        if index.column() == COLUMN_INDEX_OF_VALUE_HEX and role == Qt.EditRole:
            return True
        else:
            return False


    def setValueHex(self, index, value) -> bool:
        setDataResult = False

        str = value.replace("0x", "")

        if str.isnumeric():
            setDataResult = True
            valueRow = self.valuesList[index.row()]
            valueRow["valueHex"] = value

        return setDataResult


    def flags(self, index) -> int:
        flags = QAbstractTableModel.flags(self, index)
        if index.isValid():
            return flags | Qt.ItemIsEditable
        else:
            return flags


    def insertColumn(self, parent) -> None:
        self.insertColumns(1, 1, parent)


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

        for i in range(startRow + count - 1, startRow - 1, -1):
            self.valuesList.remove(self.valuesList[i])

        self.rows -= count
        self.endRemoveRows()
