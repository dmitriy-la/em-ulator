import gettext

from PyQt5.Qt import Qt
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtGui import QBrush

_ = gettext.gettext


ROW_INDEX_OF_FIELD_TITLE = 0
ROW_INDEX_OF_FIELD_LENGTH = 1
ROW_INDEX_OF_FIELD_ROLE = 2
ROW_INDEX_OF_FIELD_TO_BE_COPIED_IN_AUTORESP = 3
ROW_INDEX_OF_FIELD_TO_BE_SWAP_WITH_IN_AUTORESP = 4
ROW_INDEX_OF_FIRST_FIELD_VALUE = 5

NONE_VALUE_ROWS_COUNT = 5


class DataModelMsgType(QAbstractTableModel):
    def __init__(self, msgTypeTitle: str, parent=None):
        super(DataModelMsgType, self).__init__(parent)
        self.msgTypeTitle = msgTypeTitle
        self.rows = 5
        self.fieldDescrList = []

        self.isReceipt = False
        self.sendAllowed = True
        self.fieldExcludedFromLenCount = ""

        self.firstFieldTitleInGroup = ''
        self.lastFieldTitleInGroup = ''
        self.separator = ''

        self.lengthDisplayModeBytes = False


    def changeLengthDisplayMode(self) -> None:
        self.lengthDisplayModeBytes = not self.lengthDisplayModeBytes
        self.layoutChanged().emit()


    def setData(self, index, value, role) -> bool:
        setDataResult = False

        if not index.isValid():
            setDataResult = False
        elif self.editingFieldTitle(index):
            setDataResult = self.setFieldTitle(index, value)
        elif self.editingFieldLength(index, value):
            setDataResult = self.setFieldLength(index, value)
        elif self.editingFieldRole(index, value):
            setDataResult = self.setFieldRole(index, value)
        elif self.editingIfFieldToBeCopiedInAutoResp(index):
            setDataResult = self.setIfFieldToBeCopiedInAutoResp(index, value)
        elif self.editingFieldToSwapWithInAutoresp(index, role):
            setDataResult = self.setFieldToSwapWithInAutoresp(index, value)
        elif self.editingFieldValues(index, role):
            setDataResult = self.editFieldValue(index, value)
        return setDataResult



    def editingFieldTitle(self, index) -> bool:
        if index.row() == ROW_INDEX_OF_FIELD_TITLE:
            return True
        else:
            return False


    def setFieldTitle(self, index, value) -> bool:
        field = self.fieldDescrList[index.column()]
        field["fieldTitle"] = value
        return True


    def editingFieldLength(self, index, role) -> bool:
        if index.row() == ROW_INDEX_OF_FIELD_LENGTH and role != Qt.DisplayRole:
            return True
        else:
            return False


    def setFieldLength(self, index, value) -> bool:
        if value.isdigit():
            field = self.fieldDescrList[index.column()]
            if self.lengthDisplayModeBytes:
                field["fieldLength"] = str(8 * int(value))
            else:
                field["fieldLength"] = value
            setResult = True
        else:
            print("That's not a digit...")
            setResult = False

        return setResult


    def editingFieldRole(self, index, role) -> bool:
        if index.row() == ROW_INDEX_OF_FIELD_ROLE and role != Qt.DisplayRole:
            return True
        else:
            return False


    def setFieldRole(self, index, value) -> bool:
        lastFieldDescrIndex = len(self.fieldDescrList) - 1

        if value != 'roleCrc' and index.column() != lastFieldDescrIndex:
            field = self.fieldDescrList[index.column()]
            field["fieldRole"] = value
            return True
        else:
            return False


    def editingIfFieldToBeCopiedInAutoResp(self, index) -> bool:
        if index.row() == ROW_INDEX_OF_FIELD_TO_BE_COPIED_IN_AUTORESP:
            return True
        else:
            return False


    def setIfFieldToBeCopiedInAutoResp(self, index, value) -> bool:
        field = self.fieldDescrList[index.column()]
        field["fieldToBeCopiedInAutoResp"] = value
        return True


    def editingFieldToSwapWithInAutoresp(self, index, role) -> bool:
        if index.row() == 4 and role == Qt.EditRole:
            return True
        else:
            return False


    def setFieldToSwapWithInAutoresp(self, index, value) -> bool:
        field = self.fieldDescrList[index.column()]
        if field["fieldRole"] != 'roleOther':
            return False
        else:
            field["fieldToSwapWithInAutoresp"] = value
            return True


    def editingFieldValues(self, index, role) -> bool:
        field = self.fieldDescrList[index.column()]
        fieldRowsCount = NONE_VALUE_ROWS_COUNT + len(field["fieldValuesList"])

        if index.row() in range(NONE_VALUE_ROWS_COUNT, fieldRowsCount + 1) and role != Qt.DisplayRole:
            return True
        else:
            return False


    def editFieldValue(self, index, value) -> bool:
        if value == '':
            result = self.removeFieldValue(index)
        else:
            result = self.setFieldValue(index, value)

        return result


    def setFieldValue(self, index, value) -> bool:
        setResult = False

        field = self.fieldDescrList[index.column()]
        fieldLength = field["fieldLength"]

        if fieldLength != "undef." and self.newFieldValueIsValid(index, value):
            setResult = True
            self.updateFieldValue(index, value)

        return setResult


    def newFieldValueIsValid(self, index, value) -> bool:
        if (self.enteredStringForNewFieldValueIsValid(value) and
                self.newValueIsNotInUseAlready(index, value) and
                self.newValueWithinFieldLengthRange(index, value)):
            return True
        else:
            return False



    def updateFieldValue(self, index, value) -> None:
        field = self.fieldDescrList[index.column()]
        fieldValuesList = field["fieldValuesList"]
        fieldValuesCount = len(fieldValuesList)

        if index.row() - 4 > fieldValuesCount:
            fieldValuesList.append({"valueHex": " ", "valueMeaning": " "})

        currentFieldValue = fieldValuesList[index.row() - NONE_VALUE_ROWS_COUNT]

        if isinstance(currentFieldValue, dict):
            self.updateFieldValueAsDict(index, value)
        elif isinstance(currentFieldValue, str):
            self.updateFieldValueAsStr(index, value)


    def updateFieldValueAsStr(self, index, value) -> None:
        parsedList = value.split(" - ", 1)
        enteredHexStrForNewValue = parsedList[0]
        enteredStrForNewValueMeaning = parsedList[1]

        field = self.fieldDescrList[index.column()]
        hexLen = int(field["fieldLength"]) // 4

        newStrHex = enteredHexStrForNewValue[:hexLen]
        newFieldValue = newStrHex + ' - ' + enteredStrForNewValueMeaning

        fieldValuesList = field["fieldValuesList"]
        fieldValuesList[index.row() - NONE_VALUE_ROWS_COUNT] = newFieldValue


    def updateFieldValueAsDict(self, index, value) -> None:
        field = self.fieldDescrList[index.column()]
        fieldValuesList = field["fieldValuesList"]

        newStrValueHex = self.getStrHexForNewValue(index, value)

        currentFieldValue = fieldValuesList[index.row() - NONE_VALUE_ROWS_COUNT]
        currentFieldValue["valueHex"] = newStrValueHex

        parsedList = value.split(" - ", 1)
        if len(parsedList) == 2:
            enteredStrForNewValueMeaning = parsedList[1]
            currentFieldValue["valueMeaning"] = enteredStrForNewValueMeaning
        else:
            currentFieldValue["valueMeaning"] = ''


    def getStrHexForNewValue(self, index, value) -> str:
        field = self.fieldDescrList[index.column()]

        parsedList = value.split(" - ", 1)
        enteredHexStrForNewValue = parsedList[0]

        intFieldLength = int(field["fieldLength"])
        if intFieldLength % 8 != 0:
            hexLen = intFieldLength // 4 + 1
        else:
            hexLen = intFieldLength // 4

        newStrValueHex = '{:0{}X}'.format(int(enteredHexStrForNewValue, 16), hexLen)

        return newStrValueHex


    def newValueIsNotInUseAlready(self, index, value) -> bool:
        parsedList = value.split(" - ", 1)
        enteredHexStrForNewValue = parsedList[0]

        field = self.fieldDescrList[index.column()]
        fieldValuesList = field["fieldValuesList"]

        if len(fieldValuesList) == 0:
            return True

        listOfFieldValuesStr = list(map(self.getFieldValueHexFromFieldValue, fieldValuesList))
        listOfFieldValuesStr.append(enteredHexStrForNewValue.zfill(int(field["fieldLength"]) // 4))

        setOfFieldValuesStr = set(listOfFieldValuesStr)

        fieldValueIndex = index.row() - NONE_VALUE_ROWS_COUNT

        if fieldValueIndex < len(fieldValuesList):
            valueHex = fieldValuesList[fieldValueIndex]["valueHex"]
        else:
            valueHex = ""

        if valueHex == enteredHexStrForNewValue:
            result = True
        else:
            if len(setOfFieldValuesStr) == len(listOfFieldValuesStr):
                result = True
            else:
                result = False

        return result


    def getFieldValueHexFromFieldValue(self, fieldValue) -> str:
        if isinstance(fieldValue, dict):
            return fieldValue["valueHex"]
        if isinstance(fieldValue, str):
            return fieldValue.split(" - ")[0]


    def removeFieldValue(self, index) -> bool:
        field = self.fieldDescrList[index.column()]
        fieldValuesList = field["fieldValuesList"]
        fieldValuesListCount = len(fieldValuesList)
        valueIndexInValuesList = index.row() - NONE_VALUE_ROWS_COUNT

        if fieldValuesListCount > 0 and valueIndexInValuesList < fieldValuesListCount:
            fieldValuesList.pop(valueIndexInValuesList)
            return True
        else:
            return False


    def enteredStringForNewFieldValueIsValid(self, value) -> bool:
        parsedList = value.split(" - ", 1)

        result = False

        if len(parsedList) == 2 or len(parsedList) == 1:
            if parsedList[0] != '':
                try:
                    int(parsedList[0], 16)
                    result = True
                except ValueError:
                    result = False

        return result


    def newValueWithinFieldLengthRange(self, index, value) -> bool:
        result = False

        parsedList = value.split(" - ", 1)

        intNewValue = int(parsedList[0], 16)

        field = self.fieldDescrList[index.column()]
        intFieldLength = int(field["fieldLength"])

        maxValueForFieldLength = 2 ** intFieldLength

        if intNewValue < maxValueForFieldLength:
            result = True

        return result


    def rowCount(self, parent=None) -> int:
        return self.rows


    def columnCount(self, parent=None) -> int:
        return len(self.fieldDescrList)


    def headerData(self, section, orientation, role) -> QVariant:
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            return section

        if section == ROW_INDEX_OF_FIELD_TITLE:
            return _("Title")
        if section == ROW_INDEX_OF_FIELD_LENGTH:
            if self.lengthDisplayModeBytes:
                return _("Length, byte")
            else:
                return _("Length, bit")
        if section == ROW_INDEX_OF_FIELD_ROLE:
            return _("Role")
        if section == ROW_INDEX_OF_FIELD_TO_BE_COPIED_IN_AUTORESP:
            return _("Copy field")
        if section == ROW_INDEX_OF_FIELD_TO_BE_SWAP_WITH_IN_AUTORESP:
            return _("Swap with")
        if section == ROW_INDEX_OF_FIRST_FIELD_VALUE:
            return _("Values")

        return QVariant()


    def appendFieldDescriptor(self, fieldDict: dict) -> None:
        self.insertColumn(len(self.fieldDescrList), fieldDict)

        fieldRowsCount = NONE_VALUE_ROWS_COUNT + len(fieldDict["fieldValuesList"])

        if self.rows < fieldRowsCount:
            self.beginInsertRows(QModelIndex(), self.rows, fieldRowsCount - 1)
            self.rows = fieldRowsCount
            self.endInsertRows()


    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role == Qt.DisplayRole or role == Qt.EditRole:
            data = self.getData(index)
            return data
        elif role == Qt.BackgroundRole:
            if self.indexIsOfCellInGroupedField(index):
                return QBrush(Qt.yellow)
        else:
            return QVariant()


    def getData(self, index) -> str:
        field = self.fieldDescrList[index.column()]
        fieldRowsCount = NONE_VALUE_ROWS_COUNT + len(field["fieldValuesList"])

        if index.row() == ROW_INDEX_OF_FIELD_TITLE:
            fieldTitle = field["fieldTitle"]
            return fieldTitle
        elif index.row() == ROW_INDEX_OF_FIELD_LENGTH:
            fieldLength = self.getFieldLength(index)
            return fieldLength
        elif index.row() == ROW_INDEX_OF_FIELD_ROLE:
            fieldRole = field["fieldRole"]
            return fieldRole
        elif index.row() == ROW_INDEX_OF_FIELD_TO_BE_COPIED_IN_AUTORESP:
            fieldToBeCopiedInAutoResp = field["fieldToBeCopiedInAutoResp"]
            return fieldToBeCopiedInAutoResp
        elif index.row() == ROW_INDEX_OF_FIELD_TO_BE_SWAP_WITH_IN_AUTORESP:
            fieldToSwapWithInAutoresp = field["fieldToSwapWithInAutoresp"]
            return fieldToSwapWithInAutoresp
        elif index.row() in range(NONE_VALUE_ROWS_COUNT, fieldRowsCount):
            valueStr = self.getFieldValueStr(index)
            return valueStr


    def getFieldValueStr(self, index) -> str:
        fieldValue = self.getFieldValue(index)

        if isinstance(fieldValue, str):
            valueStr = str()
        else:
            valueStr = str(fieldValue["valueHex"])
            valueStr += ' - '
            valueStr += str(fieldValue["valueMeaning"])

        return valueStr


    def getFieldValue(self, index) -> str:
        field = self.fieldDescrList[index.column()]
        fieldValuesList = field["fieldValuesList"]
        fieldValueIndex = index.row() - NONE_VALUE_ROWS_COUNT
        fieldValue = fieldValuesList[fieldValueIndex]

        return fieldValue


    def getFieldLength(self, index) -> str:
        field = self.fieldDescrList[index.column()]

        if self.lengthDisplayModeBytes:
            fieldLength = field["fieldLength"]
            if fieldLength != "undef.":
                return str(int(fieldLength) / 8)
            else:
                return field["fieldLength"]
        else:
            return field["fieldLength"]


    def indexIsOfCellInGroupedField(self, index) -> bool:
        startColOfGroup = self.getColNumOffirstFieldTitleInGroup()
        endColOfGroup = self.getColNumOflastFieldTitleInGroup()

        if index.column() in range(startColOfGroup, endColOfGroup + 1):
            return True
        else:
            return False


    def getColNumOffirstFieldTitleInGroup(self) -> int:
        colNumOffirstFieldTitleInGroup = -1

        for field in self.fieldDescrList:
            if field["fieldTitle"] == self.firstFieldTitleInGroup:
                colNumOffirstFieldTitleInGroup = self.fieldDescrList.index(field)

        return colNumOffirstFieldTitleInGroup


    def getColNumOflastFieldTitleInGroup(self) -> int:
        colNumOflastFieldTitleInGroup = -1

        for field in self.fieldDescrList:
            if field["fieldTitle"] == self.lastFieldTitleInGroup:
                colNumOflastFieldTitleInGroup = self.fieldDescrList.index(field)

        return colNumOflastFieldTitleInGroup


    def flags(self, index) -> int:
        flags = Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if index.isValid():
            if index.row() == ROW_INDEX_OF_FIELD_TO_BE_COPIED_IN_AUTORESP or \
               index.row() == ROW_INDEX_OF_FIELD_TO_BE_SWAP_WITH_IN_AUTORESP:
                flags = self.getFlagsForFieldToSwapWith(index)

        return flags


    def getFlagsForFieldToSwapWith(self, index) -> int:
        fieldDescr = self.fieldDescrList[index.column()]
        fieldRole = fieldDescr["fieldRole"]

        flags = Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

        if fieldRole != 'roleOther':
            flags = flags & ~Qt.ItemIsEditable & ~Qt.ItemIsEnabled
        else:
            flags = Qt.ItemIsEditable | Qt.ItemIsEnabled

        return flags


    def supportedDropActions(self):
        return Qt.MoveAction


    def setItemData(self, index, roles) -> bool:
        if not roles.contains(Qt.EditRole) and not roles.contains(Qt.DisplayRole):
            return False

        field = self.fieldDescrList[index.column()]
        fieldRowsCount = NONE_VALUE_ROWS_COUNT + len(field["fieldValuesList"])

        displayRole = str(roles[Qt.DisplayRole])

        if index.row() == ROW_INDEX_OF_FIELD_TITLE:
            field["fieldTitle"] = displayRole
        elif index.row() == ROW_INDEX_OF_FIELD_LENGTH:
            field["fieldLength"] = displayRole
        elif index.row() == ROW_INDEX_OF_FIELD_ROLE:
            field["fieldRole"] = displayRole
        elif index.row() == ROW_INDEX_OF_FIELD_TO_BE_COPIED_IN_AUTORESP:
            field["fieldToBeCopiedInAutoResp"] = displayRole
        elif index.row() == ROW_INDEX_OF_FIELD_TO_BE_SWAP_WITH_IN_AUTORESP:
            field["fieldToSwapWithInAutoresp"] = displayRole
        elif index.row() in range(NONE_VALUE_ROWS_COUNT, fieldRowsCount):
            self.setItemDataForFieldValue(index, roles)
        return True


    def setItemDataForFieldValue(self, index, roles) -> None:
        displayRole = str(roles[Qt.DisplayRole])
        valuesStr = ''

        field = self.fieldDescrList[index.column()]
        fieldValuesList = field["fieldValuesList"]
        valueIndex = index.row() - NONE_VALUE_ROWS_COUNT
        fieldValue = fieldValuesList[valueIndex]

        if isinstance(fieldValue, str):
            valuesStr += str(fieldValue)
            fieldValue = displayRole
        else:
            fieldValue["valueHex"] = displayRole
            fieldValue["valueMeaning"] = displayRole


    def insertColumn(self, column, fieldDescr) -> None:
        return self.insertColumns(column, 1, fieldDescr)


    def insertColumns(self, column, count, fieldDescr) -> None:
        self.beginInsertColumns(QModelIndex(), column, column + count - 1)

        for i in range(count):
            self.fieldDescrList.insert(column, fieldDescr)

        self.endInsertColumns()


    def removeColumn(self, column) -> bool:
        self.removeColumns(column, 1)
        return True


    def removeColumns(self, column, count) -> bool:
        self.beginRemoveColumns(QModelIndex(), column, column + count - 1)

        for i in range(count):
            self.fieldDescrList.pop(column)

        self.endRemoveColumns()

        return True


    def moveColumn(self, srcParent, srcColumn, dstParent, dstChild) -> bool:
        if srcColumn == dstChild:
            return False

        self.beginMoveColumns(QModelIndex(), srcColumn, srcColumn, QModelIndex(), dstChild)

        if dstChild < srcColumn:
            self.fieldDescrList.insert(dstChild, self.fieldDescrList[srcColumn])
            self.fieldDescrList.pop(srcColumn + 1)
        else:
            self.fieldDescrList.insert(dstChild + 1, self.fieldDescrList[srcColumn])
            self.fieldDescrList.pop(srcColumn)

        self.endMoveColumns()

        return True


    def insertRow(self, row, rowStr) -> bool:
        self.beginInsertRows(QModelIndex(), row, row)
        self.endInsertRos()
        return True


    def removeRows(self, startRow, count) -> bool:
        self.beginRemoveRows(QModelIndex(), startRow, startRow + count - 1)

        for fieldDescr in self.fieldDescrList:
            fieldDescr["fieldValuesList"].clear()
        self.rows -= count

        self.endRemoveRows()

        return True
