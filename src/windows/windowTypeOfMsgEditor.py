import copy
import gettext

from PyQt5.Qt import Qt
from PyQt5.QtCore import QModelIndex, QSize, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableView
from PyQt5.QtWidgets import QCheckBox, QComboBox, QGroupBox, QLabel, QLineEdit, QPushButton, QSpinBox
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QInputDialog, QMessageBox


import src.datamodels.dataModelMsgType as dataModelMsgType
import src.datamodels.dataModelValues as dataModelValues
import src.delegates.delegateCheckBox as delegateCheckBox
import src.delegates.delegateComboBox as delegateComboBox
import src.handlers.handlerMsgCreator as handlerMsgCreator
import src.managers.managerMsgFormats as managerMsgFormats
import src.windows.windowFieldEditor as windowFieldEditor
import src.windows.windowProfiledWindow as windowProfiledWindow


_ = gettext.gettext


class WindowTypeOfMsgEditor(windowProfiledWindow.WindowProfiledWindow):
    signalMsgTypeEditorWindowClosed = pyqtSignal()

    def __init__(self, profileTitle: str, msgType='', parent=None):
        super().__init__(profileTitle, parent)
        self.msgTypeTitle = msgType
        self.fieldsModel = dataModelMsgType.DataModelMsgType(self.msgTypeTitle)
        self.valueModel = dataModelValues.DataModelValues()

        self.initUI()

        self.workingInEditMode = False

        if self.msgTypeTitle == "":
            self.workingInEditMode = False
            self.buttonSaveAs.hide()
        else:
            self.workingInEditMode = True
            self.textEditTypeTitle.setEnabled(False)
            self.setDataForMsgType(self.msgTypeTitle)


    def initUI(self):
        self.setWindowProperties()

        principalLayout = QHBoxLayout(self)

        self.principalGroupBox = self.addPrincipalGroupBox(principalLayout)

        vLayout = self.getLayoutForPrincipalGroupBox()

        self.addLabelMsgType(vLayout)
        self.textEditTypeTitle = self.addTextEditTypeTitle(vLayout)

        self.addButtonsForFieldManaging(vLayout)
        self.addLabelMsgTypeStructure(vLayout)

        self.addTableViewSection(vLayout)

        self.labelFieldSeparator = self.addLabelFieldSeparator(vLayout)
        self.labelExampleMsg = self.addLabelExampleMsg(vLayout)

        self.addCheckBoxesWithOptions(vLayout)

        self.addButtonsSaveAsAndSaveAndClose(vLayout)

        self.show()


    def setWindowProperties(self):
        self.windowTitle = _('Message Type Editor')
        self.setWindowTitle(self.windowTitle)

        xCoord = 200
        yCoord = 200
        width = 777
        height = 500
        self.setGeometry(xCoord, yCoord, width, height)

        flags = self.windowFlags()
        self.setWindowFlags(int(flags) | Qt.Tool)

        self.setFocusPolicy(Qt.ClickFocus)
        self.setModal(True)


    def addPrincipalGroupBox(self, principalLayout):
        principalGroupBox = QGroupBox(self)
        principalGroupBox.setTitle(_('MSG editor'))

        principalLayout.addWidget(principalGroupBox)

        return principalGroupBox


    def getLayoutForPrincipalGroupBox(self):
        vLayout = QVBoxLayout(self.principalGroupBox)
        self.principalGroupBox.setLayout(vLayout)

        return vLayout


    def addLabelMsgType(self, vLayout):
        labelMsgType = QLabel(self.principalGroupBox)
        labelMsgType.setText(_('Message type title:'))
        vLayout.addWidget(labelMsgType)


    def addTextEditTypeTitle(self, vLayout):
        textEditTypeTitle = QLineEdit(self.principalGroupBox)
        textEditTypeTitle.setText(_('Type 1'))
        vLayout.addWidget(textEditTypeTitle)

        return textEditTypeTitle


    def addButtonsForFieldManaging(self, vLayout):
        hLayoutFieldManager = QHBoxLayout(self.principalGroupBox)

        self.addButtonAddField(hLayoutFieldManager)
        self.addButtonRemoveField(hLayoutFieldManager)
        self.addButtonClearAll(hLayoutFieldManager)
        self.addButtonGroupFields(hLayoutFieldManager)

        vLayout.addLayout(hLayoutFieldManager)


    def addButtonGroupFields(self, hLayoutFieldManager):
        buttonGroupFieldsInMsgType = QPushButton(self.principalGroupBox)
        buttonGroupFieldsInMsgType.setText(_('Group selected fields'))
        buttonGroupFieldsInMsgType.clicked.connect(self.onClickGroupFields)

        pixmap = QPixmap('../icons/connected.png')
        saveIcon = QIcon(pixmap)
        buttonGroupFieldsInMsgType.setIcon(saveIcon)
        buttonGroupFieldsInMsgType.setIconSize(QSize(15, 15))

        hLayoutFieldManager.addWidget(buttonGroupFieldsInMsgType)


    def addButtonClearAll(self, hLayoutFieldManager):
        buttonClearAll = QPushButton(self.principalGroupBox)
        buttonClearAll.setText(_('Clear all'))
        buttonClearAll.clicked.connect(self.onClickDelAllFields)

        pixmap = QPixmap('../icons/broom.png')
        saveIcon = QIcon(pixmap)
        buttonClearAll.setIcon(saveIcon)
        buttonClearAll.setIconSize(QSize(15, 15))

        hLayoutFieldManager.addWidget(buttonClearAll)


    def addButtonRemoveField(self, hLayoutFieldManager):
        buttonRemoveField = QPushButton(self.principalGroupBox)
        buttonRemoveField.setText(_('Remove field'))
        buttonRemoveField.clicked.connect(self.onClickDelField)

        pixmap = QPixmap('../icons/trash.png')
        saveIcon = QIcon(pixmap)
        buttonRemoveField.setIcon(saveIcon)
        buttonRemoveField.setIconSize(QSize(15, 15))

        hLayoutFieldManager.addWidget(buttonRemoveField)


    def addButtonAddField(self, hLayoutFieldManager):
        buttonAddField = QPushButton(self.principalGroupBox)
        buttonAddField.setText(_('Add field'))
        buttonAddField.clicked.connect(self.onClickStartFieldEditorWindow)

        pixmap = QPixmap('../icons/add-document.png')
        saveIcon = QIcon(pixmap)
        buttonAddField.setIcon(saveIcon)
        buttonAddField.setIconSize(QSize(15, 15))

        hLayoutFieldManager.addWidget(buttonAddField)


    def addLabelMsgTypeStructure(self, vLayout):
        labelMsgTypeStructure = QLabel(self.principalGroupBox)
        labelMsgTypeStructure.setText(_('Message structure:'))

        vLayout.addWidget(labelMsgTypeStructure)


    def addTableViewSection(self, vLayout):
        self.tableView = self.addTableViewForMsgTypeStructure(vLayout)
        self.selModel = self.tableView.selectionModel()
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        hHeader = self.tableView.horizontalHeader()
        hHeader.sectionMoved.connect(self.onClickMoveField)


    def addTableViewForMsgTypeStructure(self, vLayout):
        tableView = QTableView(self.principalGroupBox)
        tableView.setModel(self.fieldsModel)
        tableView.setToolTip(_('Table is fully editable'))

        tableView.setSelectionBehavior(QAbstractItemView.SelectColumns)

        tableView.verticalHeader().sectionClicked.connect(self.changeLengthDisplayMode)

        tableView.horizontalHeader().setSectionsMovable(True)
        tableView.horizontalHeader().setStretchLastSection(True)
        tableView.setDragEnabled(True)
        tableView.setAcceptDrops(True)

        vLayout.addWidget(tableView)

        return tableView


    def addLabelFieldSeparator(self, vLayout):
        labelFieldSeparator = QLabel(self.principalGroupBox)
        labelFieldSeparator.setText(_('Separator: not needed'))
        labelFieldSeparator.hide()

        vLayout.addWidget(labelFieldSeparator)

        return labelFieldSeparator


    def addLabelExampleMsg(self, vLayout):
        labelExampleMsg = QLabel(self.principalGroupBox)
        labelExampleMsg.setText(_('MSG example: '))

        vLayout.addWidget(labelExampleMsg)

        return labelExampleMsg


    def addCheckBoxesWithOptions(self, vLayout):
        self.addHLayoutExcludeFieldFromLengthCount(vLayout)
        self.addCheckBoxForbidSendingFromImit(vLayout)
        self.addCheckBoxMarkAsReceipt(vLayout)


    def addHLayoutExcludeFieldFromLengthCount(self, vLayout):
        hLayoutExcludeFieldFromLengthCount = QHBoxLayout(self.principalGroupBox)

        self.checkBoxExcludeFieldFromLengthCount = QCheckBox(self.principalGroupBox)
        self.checkBoxExcludeFieldFromLengthCount.setText(_('Don\'t count length of field'))
        hLayoutExcludeFieldFromLengthCount.addWidget(self.checkBoxExcludeFieldFromLengthCount)

        self.comboBoxFieldToExcludeFromLenCount = QComboBox(self.principalGroupBox)
        self.comboBoxFieldToExcludeFromLenCount.addItem('')
        self.comboBoxFieldToExcludeFromLenCount.setFixedWidth(100)
        hLayoutExcludeFieldFromLengthCount.addWidget(self.comboBoxFieldToExcludeFromLenCount)

        hLayoutExcludeFieldFromLengthCount.addSpacing(5)
        self.addLabelInLengthCount(hLayoutExcludeFieldFromLengthCount)
        hLayoutExcludeFieldFromLengthCount.addStretch(1)

        vLayout.addLayout(hLayoutExcludeFieldFromLengthCount)


    def addCheckBoxForbidSendingFromImit(self, vLayout):
        self.checkBoxForbidSendingFromImit = QCheckBox(self.principalGroupBox)
        self.checkBoxForbidSendingFromImit.setText(_('Forbid sending this MSG type'))

        vLayout.addWidget(self.checkBoxForbidSendingFromImit)


    def addCheckBoxMarkAsReceipt(self, vLayout):
        self.checkBoxMarkAsReceipt = QCheckBox(self.principalGroupBox)
        self.checkBoxMarkAsReceipt.setText(_('Message is receipt'))

        vLayout.addWidget(self.checkBoxMarkAsReceipt)


    def addLabelInLengthCount(self, hLayoutExcludeFieldFromLengthCount):
        labelInLengthCount = QLabel(self.principalGroupBox)
        labelInLengthCount.setText(_('when automatically counting length'))
        hLayoutExcludeFieldFromLengthCount.addWidget(labelInLengthCount)


    def addButtonsSaveAsAndSaveAndClose(self, vLayout):
        hButtonLayout = QHBoxLayout()
        hButtonLayout.addStretch(1)
        self.buttonSaveAs = QPushButton("Save as...")
        self.buttonSaveAs.clicked.connect(self.onClickSaveAsNewMsgType)
        hButtonLayout.addWidget(self.buttonSaveAs)

        self.buttonSave.clicked.connect(self.onClickSaveMsgType)
        hButtonLayout.addWidget(self.buttonSave)

        hButtonLayout.addWidget(self.buttonClose)

        vLayout.addLayout(hButtonLayout)


    def setDataForMsgType(self, msgType=''):
        if msgType == '':
            return

        self.initialMsgTypeDict = copy.deepcopy(self.formatManager.getInfoForMsgType(msgType))

        self.setTextEditTypeTitle(self.initialMsgTypeDict)
        self.setCheckBoxMarkAsReceipt(self.initialMsgTypeDict)
        self.setCheckBoxForbidSending(self.initialMsgTypeDict)
        self.setGroupedFields(self.initialMsgTypeDict)
        self.setSeparator(self.initialMsgTypeDict)

        self.prepareComboBoxFieldToExcludeFromLenCount(self.initialMsgTypeDict)
        self.setCheckBoxExcludeFieldFromLengthCount(self.initialMsgTypeDict)

        self.addRoleComboBoxesToRow(2)
        self.addCheckBoxToRow(3)
        self.addSwapFieldsComboBoxesToRow(4)

        self.createExampleMsgByDict(self.initialMsgTypeDict)


    def setCheckBoxExcludeFieldFromLengthCount(self, msgTypeDict: dict):
        if msgTypeDict["fieldExcludedFromLenCount"] != '':
            self.checkBoxExcludeFieldFromLengthCount.setChecked(True)
            index = self.comboBoxFieldToExcludeFromLenCount.findText(msgTypeDict["fieldExcludedFromLenCount"])
            self.comboBoxFieldToExcludeFromLenCount.setCurrentIndex(index)
        else:
            self.checkBoxExcludeFieldFromLengthCount.setChecked(False)


    def prepareComboBoxFieldToExcludeFromLenCount(self, msgTypeDict: dict):
        for msgDescr in msgTypeDict["fieldDescrsList"]:
            self.comboBoxFieldToExcludeFromLenCount.addItem(msgDescr["fieldTitle"])
            self.fieldsModel.appendFieldDescriptor(msgDescr)


    def setSeparator(self, msgTypeDict: dict):
        if msgTypeDict["separator"] != '':
            self.labelFieldSeparator.setText(msgTypeDict["separator"])


    def setTextEditTypeTitle(self, msgTypeDict: dict):
        self.textEditTypeTitle.setText(msgTypeDict["msgTypeTitle"])


    def setGroupedFields(self, msgTypeDict: dict):
        self.fieldsModel.firstFieldTitleInGroup = msgTypeDict["firstFieldTitleInGroup"]
        self.fieldsModel.lastFieldTitleInGroup = msgTypeDict["lastFieldTitleInGroup"]


    def setCheckBoxForbidSending(self, msgTypeDict: dict):
        # inverted
        if msgTypeDict["sendAllowed"]:
            self.checkBoxForbidSendingFromImit.setChecked(False)
        else:
            self.checkBoxForbidSendingFromImit.setChecked(True)


    def setCheckBoxMarkAsReceipt(self, msgTypeDict: dict):
        if msgTypeDict["isReceipt"]:
            self.checkBoxMarkAsReceipt.setChecked(True)
        else:
            self.checkBoxMarkAsReceipt.setChecked(False)


    @pyqtSlot()
    def onClickCheckboxUndefLength(self):
        if self.checkBoxMarkFieldLengthAsUndefined.isChecked():
            self.spinBoxLength.setDisabled(True)
        else:
            self.spinBoxLength.setEnabled(True)


    @pyqtSlot()
    def onLengthChanged(self):
        valueMax = 1
        if self.spinBoxLength.value() < 32:
            valueMax = pow(2, self.spinBoxLength.value())
            valueMax -= 1
        else:
            valueMax = self.spinBoxValueHex.maximum()

        self.spinBoxValueHex.setRange(0, valueMax)


    @pyqtSlot()
    def onClickAddField(self):
        self.addNewField()


    @pyqtSlot()
    def onClickClearAllRows(self):
        rowCount = self.valueModel.rows
        self.valueModel.removeRows(0, rowCount)
        self.spinBoxValueHex.setValue(0)


    def incrementValueHex(self):
        newLengthValue = self.spinBoxValueHex.value()
        newLengthValue += 1
        self.spinBoxValueHex.setValue(newLengthValue)


    @pyqtSlot(dict)
    def addNewField(self, fieldDescr: dict):
        self.fieldsModel.appendFieldDescriptor(fieldDescr)

        self.comboBoxFieldToExcludeFromLenCount.addItem(fieldDescr["fieldTitle"])

        self.addRoleComboBoxesToRow(2)
        self.addCheckBoxToRow(3)

        delegate = self.tableView.itemDelegateForRow(4)
        if delegate:
            delegate.deleteLater()

        self.addSwapFieldsComboBoxesToRow(4)

        dictOfNewMsgType = self.getDictOfNewMsgType()

        self.createExampleMsgByDict(dictOfNewMsgType)


    def getDictOfNewMsgType(self):
        fieldDescrsListOfNewMsgType = self.fieldsModel.fieldDescrList
        msgType = self.textEditTypeTitle.text()
        separator = self.fieldsModel.separator

        dictOfNewMsgType = {"msgTypeTitle": msgType,
                            "isReceipt": self.checkBoxMarkAsReceipt.isChecked(),
                            "sendAllowed": not (self.checkBoxForbidSendingFromImit.isChecked()),
                            "firstFieldTitleInGroup": self.fieldsModel.firstFieldTitleInGroup,
                            "lastFieldTitleInGroup": self.fieldsModel.lastFieldTitleInGroup,
                            "separator": separator,
                            "fieldExcludedFromLenCount": self.comboBoxFieldToExcludeFromLenCount.currentText(),
                            "fieldDescrsList": list(fieldDescrsListOfNewMsgType)}

        return dictOfNewMsgType


    def getFieldRole(self) -> str:
        if self.radioButtonRoleLength.isChecked():
            role = 'roleLength'
        elif self.radioButtonRoleType.isChecked():
            role = 'roleType'
        elif self.radioButtonRoleId.isChecked():
            role = 'roleId'
        elif self.radioButtonRoleCrc.isChecked():
            role = 'roleCrc'
        elif self.radioButtonRoleOther.isChecked():
            role = 'roleOther'
        else:
            role = ''

        return role


    def showInpitDialogEnterFieldSeparator(self):
        separatorDialog = self.getSeparatorDialog()

        spinBox = separatorDialog.findChild(QSpinBox)
        spinBox.setDisplayIntegerBase(16)
        # spinBox.setPrefix('0x')
        spinBox.setRange(0, 2147483647)

        result = separatorDialog.exec()
        if result:
            text = _('Separator: ')
            text += spinBox.text()
            self.labelFieldSeparator.setText(text)
            self.labelFieldSeparator.show()
            self.fieldsModel.separator = str(spinBox.text())


    def getSeparatorDialog(self):
        separatorDialog = QInputDialog(self)
        separatorDialog.setWindowTitle(_('Enter separator'))
        separatorDialog.setLabelText(_('Separator marks end of field of undefined length when:') + '\n' +
                                     _('1. Fields with undef length are inside of a group, or') + '\n' +
                                     _('2. Two or more fields with undefined length follow each other'))
        separatorDialog.setIntRange(0, 2147483647)
        separatorDialog.setIntValue(0)
        separatorDialog.setIntStep(1)
        separatorDialog.doubleMaximum()

        return separatorDialog


    def formFieldLengthString(self) -> str:
        length = ''
        if self.checkBoxMarkFieldLengthAsUndefined.isChecked():
            length += 'undef.'
        else:
            length += str(self.spinBoxLength.value())
        return length


    def resetAllEnteredData(self):
        self.checkBoxMarkFieldToBeCopiedInAutoresponse.setChecked(False)
        self.checkBoxMarkFieldToBeSwapedWithAnotherInAutoresponse.setChecked(False)
        self.checkBoxMarkFieldLengthAsUndefined.setChecked(False)

        self.spinBoxLength.setEnabled(True)
        self.spinBoxValueHex.setValue(0)

        rowCount = self.valueModel.rows
        self.valueModel.removeRows(0, rowCount)


    @pyqtSlot()
    def onClickStartFieldEditorWindow(self):
        self.fieldEditor = windowFieldEditor.WindowFieldEditor(self.profileTitle)
        self.fieldEditor.signalFieldAddedFromFieldEditor.connect(self.addNewField)


    def addRoleComboBoxesToRow(self, rowNum: int):
        choices = ['roleLength', 'roleId', 'roleType', 'roleOther', 'roleCrc']

        self.addComboBoxToRow(choices, rowNum)


    def addSwapFieldsComboBoxesToRow(self, rowNum: int):
        choices = ['']
        for fieldDescr in self.fieldsModel.fieldDescrList:
            if fieldDescr["fieldRole"] == 'roleOther':
                choices.append(fieldDescr["fieldTitle"])

        self.addComboBoxToRow(choices, rowNum)


    def addComboBoxToRow(self, choices: list, rowNum: int):
        comboBox = delegateComboBox.DelegateComboBox(self.fieldsModel, choices)

        self.tableView.setItemDelegateForRow(rowNum, comboBox)

        # make combo boxes editable with a single-click:
        for column in range(len(self.fieldsModel.fieldDescrList)):
            if self.fieldsModel.fieldDescrList[column]["fieldRole"] == 'roleOther':
                self.tableView.openPersistentEditor(self.fieldsModel.index(rowNum, column))


    def addCheckBoxToRow(self, rowNum: int):
        checkBox = delegateCheckBox.DelegateCheckBox(self.tableView)
        self.tableView.setItemDelegateForRow(rowNum, checkBox)


    @pyqtSlot()
    def onClickGroupFields(self):
        indexes = self.selModel.selectedIndexes()

        # if at least two fields selected
        if len(indexes) > 0:
            firstField = indexes[0]

            lastRowName = ''
            lastestColumn = 0

            # get title of last field in group
            for cell in indexes:
                if cell.row() == 0 and cell.column() > lastestColumn:
                    lastestColumn = cell.column()
                    lastRowName = cell.data()
                if cell.row() == 1 and cell.data() == 'undef.':
                    self.labelFieldSeparator.show()
                    self.showInpitDialogEnterFieldSeparator()

            self.fieldsModel.firstFieldTitleInGroup = firstField.data()
            self.fieldsModel.lastFieldTitleInGroup = lastRowName
        else:
            print('no')

        self.selModel.clearSelection()


    @pyqtSlot()
    def onClickSaveAsNewMsgType(self):
        self.initialMsgTypeDict = copy.deepcopy(self.formatManager.getInfoForMsgType(self.msgTypeTitle))

        self.workingInEditMode = False
        if self.userEnteredDataIsValid():
            newMsgTypeTitle = self.getNewMsgTypeTitle()
            self.textEditTypeTitle.setText(newMsgTypeTitle)

            if newMsgTypeTitle != "" and self.msgTypeTitleIsUnique():
                self.formatManager.updateMsgType(self.initialMsgTypeDict)
                self.appendNewMsgTypeToMsgFormatsFile(newMsgTypeTitle)

        self.workingInEditMode = True


    def getNewMsgTypeTitle(self):
        text, ok = QInputDialog.getText(self, _('New MSG type title'), _('Enter new MSG type title:'))

        newMsgTypeTitle = str(text)

        if not ok:
            return ""
        elif newMsgTypeTitle == "":
            self.showErrorMessageBox(_("Empty MSG type title!"))

        self.msgTypeTitle = newMsgTypeTitle

        return newMsgTypeTitle



    @pyqtSlot()
    def onClickSaveMsgType(self):
        if self.userEnteredDataIsValid() and self.msgTypeTitleIsUnique():
            self.appendNewMsgTypeToMsgFormatsFile()


    def userEnteredDataIsValid(self) -> bool:
        dataValidationResult = (self.allFieldTitlesAreUnique() and
                                self.overallMsgLengthIsMultipleOfEight() and
                                self.msgTypeFieldIsSetCorrectly() and
                                self.fieldTypeValueIsUnique() and
                                self.noUndefFieldIsPlacedInTheMiddleOfBitFields() and
                                self.fewFieldsOfUndefLengthHaveSeparator())
        if dataValidationResult:
            return True
        else:
            print("ERROR: User-entered data is not valid")
            return False


    def msgTypeFieldIsSetCorrectly(self) -> bool:
        fieldList = self.fieldsModel.fieldDescrList

        self.fieldsModel.dataChanged.emit(QModelIndex(), QModelIndex())

        errorHeader = _("Error: msg type error")
        errorText = _('Set role \'roleType\' for exactly one field with exactly one possible value')

        listOfFieldDescrsWithType = list(filter(lambda fieldDescr: fieldDescr["fieldRole"] == 'roleType', fieldList))

        if len(listOfFieldDescrsWithType) > 1 or len(listOfFieldDescrsWithType) == 0:
            self.showErrorMessageBox(errorHeader, errorText)
            return False
        elif len(listOfFieldDescrsWithType[0]["fieldValuesList"]) != 1:
            self.showErrorMessageBox(errorHeader, errorText)
            return False
        else:
            return True


    def fieldTypeValueIsUnique(self):
        formatsManager = managerMsgFormats.ManagerMsgFormats(self.profileTitle)
        listOfTypesValues = formatsManager.getListOfTypesValues()

        intListOfTypesValues = list(map(int, listOfTypesValues))

        newMsgTypeFieldTypeValue = self.getFieldTypeValue()
        intNewMsgTypeFieldTypeValue = int(newMsgTypeFieldTypeValue)

        if self.workingInEditMode:
            listOfAllMsgTypeTitles = formatsManager.getListOfAllMsgTypeTitles()
            typeIndex = listOfAllMsgTypeTitles.index(self.msgTypeTitle)
            intListOfTypesValues.pop(typeIndex)
            intListOfTypesValues.insert(typeIndex, intNewMsgTypeFieldTypeValue)
        else:
            intListOfTypesValues.append(intNewMsgTypeFieldTypeValue)

        allUniqueTypeValues = set(intListOfTypesValues)

        if len(allUniqueTypeValues) != len(intListOfTypesValues):
            errorHeader = _("Error: message type error. Value entered for message type is not unique. "
                            "Each message type should have its own value indicating its type.")
            errorText = _('Values that are already in use: ' + str(intListOfTypesValues))
            self.showErrorMessageBox(errorHeader, errorText)
            return False
        else:
            return True


    def getFieldTypeValue(self):
        fieldList = self.fieldsModel.fieldDescrList

        fieldDescrWithType = next(filter(lambda fieldDescr: fieldDescr["fieldRole"] == 'roleType', fieldList))

        fieldTypeValueAndMeaning = fieldDescrWithType["fieldValuesList"][0]
        fieldTypeValue = fieldTypeValueAndMeaning["valueHex"]

        return fieldTypeValue


    def fewFieldsOfUndefLengthHaveSeparator(self) -> bool:
        fieldList = self.fieldsModel.fieldDescrList

        fieldLengthList = [field["fieldLength"] for field in fieldList]
        listOfFieldIndexesOfUndefLength = [fieldLength for fieldLength in fieldLengthList if fieldLength == 'undef.']

        if len(listOfFieldIndexesOfUndefLength) > 1:
            if self.fieldsModel.separator == '' or self.fieldsModel.separator is None:
                self.showInpitDialogEnterFieldSeparator()

            if self.fieldsModel.separator == '':
                return False
            else:
                return True

        return True


    def noUndefFieldIsPlacedInTheMiddleOfBitFields(self) -> bool:
        result = True

        fieldDescrList = self.fieldsModel.fieldDescrList

        bitCount = 0

        for fieldDescr in fieldDescrList:
            if fieldDescr["fieldLength"] == 'undef.':
                if bitCount % 8 != 0:
                    result = False
                    self.showErrorMessageBox(_("Fields with undefined length can't be placed in the middle of bit fields."),
                                             _('Sum length of fields that come before field of undefined length must be '
                                               'multiplicity of 8 - check field\'s length.'))
                    break
                else:
                    bitCount = 0
            else:
                bitCount += int(fieldDescr["fieldLength"])

        return result


    def msgTypeTitleIsUnique(self) -> bool:
        msgTypeTitle = self.getMsgTypeTitle()

        listOfAllMsgTypeTitles = self.formatManager.getListOfAllMsgTypeTitles()

        if msgTypeTitle in listOfAllMsgTypeTitles and not self.workingInEditMode:
            userReply = QMessageBox.question(self, 'Save', _('Msg type with this title already exists! Overwright?'),
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if userReply == QMessageBox.No:
                result = False
            else:
                result = True

        else:
            result = True

        return result


    def getMsgTypeTitle(self):
        if self.workingInEditMode:
            msgTypeTitle = self.msgTypeTitle
        else:
            msgTypeTitle = self.textEditTypeTitle.text()
        return msgTypeTitle


    def overallMsgLengthIsMultipleOfEight(self) -> bool:
        overallMsgLength = self.getOverallMsgLength()

        if overallMsgLength % 8 == 0:
            result = True
        else:
            result = False
            self.showErrorMessageBox(_("Sum field length does not fit into whole byte."),
                                     _('Whole length must be multiplicity of 8 - check each field\'s length.'))

        return result


    def getOverallMsgLength(self):
        overallMsgLength = 0

        for fieldDescr in self.fieldsModel.fieldDescrList:
            if fieldDescr["fieldLength"] == 'undef.':
                continue
            else:
                overallMsgLength += int(fieldDescr["fieldLength"])

        return overallMsgLength


    def allFieldTitlesAreUnique(self) -> bool:
        listOfFieldTitles = [fieldDescr["fieldTitle"] for fieldDescr in self.fieldsModel.fieldDescrList]

        setOfUniqueFieldTitles = set(listOfFieldTitles)
        if len(listOfFieldTitles) == len(setOfUniqueFieldTitles):
            result = True
        else:
            result = False
            self.showErrorMessageBox(_("There are two or more fields with the same title."),
                                     _('Enter unique title for each field.'))

        return result


    def appendNewMsgTypeToMsgFormatsFile(self, msgTypeTitle=""):
        fieldDescrsListOfNewMsgType = self.fieldsModel.fieldDescrList

        if msgTypeTitle == "":
            msgTypeTitle = self.textEditTypeTitle.text()

        dictOfNewMsgType = {"msgTypeTitle": msgTypeTitle,
                            "isReceipt": self.checkBoxMarkAsReceipt.isChecked(),
                            "sendAllowed": not (self.checkBoxForbidSendingFromImit.isChecked()),
                            "firstFieldTitleInGroup": self.fieldsModel.firstFieldTitleInGroup,
                            "lastFieldTitleInGroup": self.fieldsModel.lastFieldTitleInGroup,
                            "separator": self.fieldsModel.separator,
                            "fieldExcludedFromLenCount": self.comboBoxFieldToExcludeFromLenCount.currentText(),
                            "fieldDescrsList": fieldDescrsListOfNewMsgType}

        self.formatManager.setCurrentProfile(self.profileTitle)
        self.formatManager.updateMsgType(dictOfNewMsgType)

        self.fieldsModel.firstFieldTitleInGroup = ''
        self.fieldsModel.lastFieldTitleInGroup = ''

        self.showSuccessMessageBox(_('Message of type \"') + msgTypeTitle + _('\" saved'))


    def createExampleMsgByDict(self, msgTypeDict: dict):
        msgCreator = handlerMsgCreator.HandlerMsgCreator(self.profileTitle)
        msgString = msgCreator.getExampleMsgFromMsgTypeDict(msgTypeDict)

        text = _('MSG example: ')
        text += str(msgString)
        self.labelExampleMsg.setText(text)


    @pyqtSlot(int)
    def changeLengthDisplayMode(self, rowIndex: int):
        if rowIndex == 1:
            self.fieldsModel.changeLengthDisplayMode()


    @pyqtSlot(int, int, int)
    def onClickMoveField(self, srcColumn: int, int2: int, dstChild: int):
        if dstChild < srcColumn:
            self.fieldsModel.insertColumn(dstChild, self.fieldsModel.fieldDescrList[srcColumn])
            srcColumn += 1
            self.fieldsModel.removeColumn(srcColumn)
        else:
            dstChild += 1
            self.fieldsModel.insertColumn(dstChild, self.fieldsModel.fieldDescrList[srcColumn])
            self.fieldsModel.removeColumn(srcColumn)


    @pyqtSlot()
    def onClickDelField(self):
        selectionModel = self.tableView.selectionModel()
        indexes = selectionModel.selectedIndexes()

        self.fieldsModel.removeColumns(indexes[0].column(), 1)


    @pyqtSlot()
    def onClickDelAllFields(self):
        allFieldsCount = len(self.fieldsModel.fieldDescrList)

        fieldDescrList = self.fieldsModel.fieldDescrList
        for fieldDescr in fieldDescrList:
            self.fieldsModel.removeRows(5, len(fieldDescr["fieldValuesList"]))

        self.fieldsModel.removeColumns(0, allFieldsCount)


    def closeEvent(self, event):
        self.signalMsgTypeEditorWindowClosed.emit()
