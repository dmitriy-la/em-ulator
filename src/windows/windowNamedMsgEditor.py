import gettext

from PyQt5.Qt import Qt
from PyQt5.QtCore import QObject, QRegExp, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QCheckBox, QComboBox, QGridLayout, QGroupBox
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QSpinBox
from PyQt5.QtWidgets import QTabBar, QTabWidget, QVBoxLayout, QWidget

import src.handlers.handlerMsgCreator as handlerMsgCreator
import src.managers.managerNamedMsg as managerNamedMsg
import src.windows.windowProfiledWindow as windowProfiledWindow


_ = gettext.gettext


class WindowNamedMsgEditor(windowProfiledWindow.WindowProfiledWindow):
    signalNamedMsgAdded = pyqtSignal(dict)

    def __init__(self, profileTitle: str, parent=None):
        super().__init__(profileTitle, parent)
        self.inProcessOfGroupingFields = False

        self.line = 0
        self.groupedFieldsLine = 0
        self.widgetInOneGroupCount = 0

        self.listWidgetTabs = []
        self.listOfFieldDescrAndWidgets = []

        self.moreThanOneFieldOfUndefLen = False

        self.initUI()


    def initUI(self):
        self.setWindowProperties()

        vLayoutPrincipal = QVBoxLayout(self)
        self.addHLayForChoosingMsgType(vLayoutPrincipal)
        self.addHLayForEnteringMsgTitle(vLayoutPrincipal)
        self.addGroupBoxForFields(vLayoutPrincipal)
        self.addLabelForResultMsg(vLayoutPrincipal)
        self.addTabsForGroupedFields(vLayoutPrincipal)

        self.addGroupBoxForGroupedFields()

        vLayoutPrincipal.addStretch(10)

        self.addHLayButtonsSaveExit(vLayoutPrincipal)

        self.show()


    def setWindowProperties(self):
        self.setModal(True)
        self.setFocusPolicy(Qt.StrongFocus)

        flags = self.windowFlags()
        self.setWindowFlags(int(flags) | Qt.Tool)

        self.setWindowTitle(_('Named Msg Editor'))


    def addHLayButtonsSaveExit(self, vLayoutPrincipal):
        hLayButtonsSaveExit = QHBoxLayout(self)

        self.buttonSave.clicked.connect(self.saveNamedMsg)
        hLayButtonsSaveExit.addWidget(self.buttonSave)
        hLayButtonsSaveExit.addWidget(self.buttonClose)

        vLayoutPrincipal.addLayout(hLayButtonsSaveExit)


    def addGroupBoxForGroupedFields(self):
        self.groupBoxGroupedFields = QGroupBox(self)

        self.gridLayGroupedFields = QGridLayout(self)

        self.groupBoxGroupedFields.setLayout(self.gridLayGroupedFields)
        self.groupBoxGroupedFields.hide()


    def addTabsForGroupedFields(self, vLayoutPrincipal):
        self.tabs = QTabWidget()
        self.tabs.hide()

        vLayoutPrincipal.addWidget(self.tabs)


    def addListMsgTypesToComboBoxWithMsgTypes(self, comboBoxMsgType):
        comboBoxMsgType.addItem('')

        listMsgTypes = self.formatManager.getListOfAllMsgTypeTitles()
        comboBoxMsgType.addItems(listMsgTypes)

        comboBoxMsgType.setCurrentIndex(0)
        comboBoxMsgType.currentTextChanged.connect(self.updateFormForMsgTypeSelected)

        return comboBoxMsgType


    def addLabelForResultMsg(self, vLayoutPrincipal):
        self.labelResultMsg = QLabel(_('MSG: '))
        self.labelResultMsg.setStyleSheet('QLabel {background-color : rgba(200, 200, 200); }')
        self.labelResultMsg.setWordWrap(True)

        vLayoutPrincipal.addWidget(self.labelResultMsg)


    def addGroupBoxForFields(self, vLayoutPrincipal):
        self.groupBoxFields = QGroupBox(self)

        self.gridLayFieldWidgets = QGridLayout(self)
        self.groupBoxFields.setLayout(self.gridLayFieldWidgets)

        self.groupBoxFields.setTitle(_('MSG fields:'))
        self.groupBoxFields.hide()

        vLayoutPrincipal.addWidget(self.groupBoxFields)


    def addHLayForEnteringMsgTitle(self, vLayoutPrincipal):
        self.labelEnterMsgTitle = QLabel(_('MSG title'))
        self.labelEnterMsgTitle.hide()

        self.lineEditMsgTitle = QLineEdit(self)
        self.lineEditMsgTitle.hide()

        hLayEnterMsgTitle = QHBoxLayout(self)
        hLayEnterMsgTitle.addWidget(self.labelEnterMsgTitle)
        hLayEnterMsgTitle.addWidget(self.lineEditMsgTitle)

        vLayoutPrincipal.addLayout(hLayEnterMsgTitle)


    def addHLayForChoosingMsgType(self, vLayoutPrincipal):
        self.comboBoxCurrentMsgType = QComboBox(self)
        self.comboBoxCurrentMsgType = self.addListMsgTypesToComboBoxWithMsgTypes(self.comboBoxCurrentMsgType)

        hLayChooseMsgType = QHBoxLayout(self)
        labelChooseMsgType = QLabel(_('Select MSG type'))
        hLayChooseMsgType.addWidget(labelChooseMsgType)

        hLayChooseMsgType.addWidget(self.comboBoxCurrentMsgType)

        vLayoutPrincipal.addLayout(hLayChooseMsgType)


    @pyqtSlot()
    def updateFormForMsgTypeSelected(self):
        """
        :return:
        """
        self.removeAllFieldWidgets()

        self.prepareWindowAndData()

        currentMsgType = self.comboBoxCurrentMsgType.currentText()

        self.moreThanOneFieldOfUndefLen = self.formatManager.thereIsMoreThanOneFieldOfUndefLengthInMsgType(currentMsgType)

        self.currentMsgDict = self.formatManager.getInfoForMsgType(currentMsgType)
        currentFieldDescrsList = self.formatManager.getFieldDescrsListForMsgType(currentMsgType)

        for fieldDescr in currentFieldDescrsList:
            widgetToAdd = self.getWidgetToAdd(fieldDescr)
            self.processFieldsWithSpecialRoles(fieldDescr, widgetToAdd)
            self.line += 1

        self.setResultingMsgString()

        self.adjustSize()


    def getWidgetToAdd(self, fieldDescr: dict) -> QWidget:
        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        if self.formatManager.fieldIsFirstFieldInGroupInMsgType(fieldDescr["fieldTitle"], currentMsgType):
            widgetToAdd = self.processFirstFieldInGroup(fieldDescr)
        elif self.inProcessOfGroupingFields:
            widgetToAdd = self.processSubsequentFieldsInGroup(fieldDescr)
        else:
            widgetToAdd = self.processRegularField(fieldDescr)

        return widgetToAdd


    def prepareWindowAndData(self):
        self.labelEnterMsgTitle.show()
        self.lineEditMsgTitle.show()
        self.groupBoxFields.show()

        self.line = 0
        self.groupedFieldsLine = 0
        self.inProcessOfGroupingFields = False
        self.widgetInOneGroupCount = 0

        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        if currentMsgType == '':
            self.labelEnterMsgTitle.hide()
            self.lineEditMsgTitle.hide()
            self.adjustSize()


    def processRegularField(self, fieldDescr) -> QWidget:
        fieldTitle = fieldDescr["fieldTitle"] + " (" + str(fieldDescr["fieldLength"]) + ")"
        labelFieldName = QLabel(fieldTitle)
        widgetToAdd = self.getWidgetForEnteringValue(fieldDescr)

        self.gridLayFieldWidgets.addWidget(labelFieldName, self.line, 0)
        self.gridLayFieldWidgets.addWidget(widgetToAdd, self.line, 1)

        fieldWidgetAndDescrDict = {"fieldDescr": fieldDescr, "widgetForFieldValue": widgetToAdd,
                                   "labelForFieldTitle": labelFieldName, "manualValueCheckBox": None}
        self.listOfFieldDescrAndWidgets.append(fieldWidgetAndDescrDict)

        return widgetToAdd


    def processSubsequentFieldsInGroup(self, fieldDescr) -> QWidget:
        fieldTitle = fieldDescr["fieldTitle"] + " (" + fieldDescr["fieldLength"] + ")"

        labelFieldTitle = QLabel(fieldTitle)
        self.listWidgetTabs[0].children()[0].addWidget(labelFieldTitle, self.groupedFieldsLine, 0)
        self.listWidgetTabs.append(labelFieldTitle)

        widgetToAdd = self.getWidgetForEnteringValue(fieldDescr)
        self.listWidgetTabs[0].children()[0].addWidget(widgetToAdd, self.groupedFieldsLine, 1)
        self.listWidgetTabs.append(widgetToAdd)

        self.groupedFieldsLine += 1

        lastFieldTitleInGroup = self.currentMsgDict["lastFieldTitleInGroup"]
        if fieldDescr["fieldTitle"] == lastFieldTitleInGroup:
            self.inProcessOfGroupingFields = False
            self.widgetInOneGroupCount = len(self.listWidgetTabs)

        fieldWidgetAndDescrDict = {"fieldDescr": fieldDescr,
                                   "widgetForFieldValue": widgetToAdd,
                                   "labelForFieldTitle": labelFieldTitle,
                                   "manualValueCheckBox": None}
        self.listOfFieldDescrAndWidgets.append(fieldWidgetAndDescrDict)

        return widgetToAdd


    def processFirstFieldInGroup(self, fieldDescr: dict):
        gridLayGroupedFields = QGridLayout(self)

        labelFieldTitle = self.getLabelFieldTitle(fieldDescr)
        gridLayGroupedFields.addWidget(labelFieldTitle, self.groupedFieldsLine, 0)

        widgetToAdd = self.getWidgetForEnteringValue(fieldDescr)
        self.listWidgetTabs.append(widgetToAdd)
        gridLayGroupedFields.addWidget(widgetToAdd, self.groupedFieldsLine, 1)

        self.gridLayFieldWidgets.addWidget(self.tabs, self.line, 0, 1, 3)

        groupBoxGroupedFields = QGroupBox(self)
        groupBoxGroupedFields.setLayout(gridLayGroupedFields)
        self.listWidgetTabs.append(groupBoxGroupedFields)

        self.inProcessOfGroupingFields = True
        self.groupedFieldsLine += 1

        fieldWidgetAndDescrDict = {"fieldDescr": fieldDescr, "widgetForFieldValue": widgetToAdd,
                                   "labelForFieldTitle": labelFieldTitle, "manualValueCheckBox": None}
        self.listOfFieldDescrAndWidgets.append(fieldWidgetAndDescrDict)

        return widgetToAdd


    def addTabForGroupedFields(self, groupBoxGroupedFields):
        self.tabs.addTab(groupBoxGroupedFields, _('Group'))
        self.tabs.addTab(QWidget(), '+')

        self.tabs.show()
        self.tabs.setTabsClosable(True)

        self.tabs.currentChanged.connect(self.addNewTab)
        self.tabs.tabCloseRequested.connect(self.closeGroupedFieldTab)

        self.tabs.tabBar().setTabButton(0, QTabBar.RightSide, QWidget())
        self.tabs.tabBar().setTabButton(0, QTabBar.LeftSide, QWidget())
        self.tabs.tabBar().setTabButton(1, QTabBar.RightSide, QWidget())
        self.tabs.tabBar().setTabButton(1, QTabBar.LeftSide, QWidget())


    def getLabelFieldTitle(self, fieldDescr):
        fieldTitle = fieldDescr["fieldTitle"] + " (" + str(fieldDescr["fieldLength"]) + ")"
        labelFieldTitle = QLabel(fieldTitle)
        self.listWidgetTabs.append(labelFieldTitle)

        return labelFieldTitle


    def processFieldsWithSpecialRoles(self, fieldDescr: dict, widgetToAdd: QWidget):
        if self.formatManager.fieldRoleIsLength(fieldDescr):
            self.proccessFieldWithRoleLength(fieldDescr, widgetToAdd)
        elif self.formatManager.fieldRoleIsId(fieldDescr):
            self.proccessFieldWithRoleIdOrCrc(fieldDescr, widgetToAdd)
        elif self.formatManager.fieldRoleIsCrc(fieldDescr):
            self.proccessFieldWithRoleIdOrCrc(fieldDescr, widgetToAdd)
        elif self.formatManager.fieldRoleIsType(fieldDescr):
            self.proccessFieldWithRoleType(fieldDescr, widgetToAdd)


    def setResultingMsgString(self):
        """

        :return:
        """
        listOfFieldValues = self.getListOfEnteredFieldsValues()
        listOfFieldValues = self.setLengthValueForFieldWithRoleLength(listOfFieldValues)

        currentMsgType = self.comboBoxCurrentMsgType.currentText()

        msgCreator = handlerMsgCreator.HandlerMsgCreator(self.profileTitle)
        msgCreator.setListOfFieldValuesFromList(listOfFieldValues)
        strExampleMsg = msgCreator.getMsgFromListOfPreviouslySetHexFieldValuesInMsgType(currentMsgType)

        self.labelResultMsg.setText(_('MSG: ') + strExampleMsg)


    def setLengthValueForFieldWithRoleLength(self, listOfFieldValues: list):
        """

        :param listOfFieldValues:
        :return:
        """
        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        fieldWithLengthIndex = self.formatManager.getIndexOfFieldWithRoleLengthInMsgType(currentMsgType)

        if fieldWithLengthIndex is not None:
            fieldDescrAndWidgetsForFieldWithLength = self.listOfFieldDescrAndWidgets[fieldWithLengthIndex]

            valueEnteredManually = fieldDescrAndWidgetsForFieldWithLength["manualValueCheckBox"].isChecked()

            if not valueEnteredManually:
                fieldDescrsList = self.currentMsgDict["fieldDescrsList"]
                fieldDescr = fieldDescrsList[fieldWithLengthIndex]
                fieldLength = fieldDescr["fieldLength"]

                msgLength = self.getLenOfCurrentMsgInBytes()
                listOfFieldValues[fieldWithLengthIndex] = '{:0{}X}'.format(msgLength, int(fieldLength) // 4)

        return listOfFieldValues


    def proccessFieldWithRoleType(self, msgDescr: dict, widgetToAdd: QWidget):
        """
        Setting fixed value in widget for field with type of msg
        :param widgetToAdd:
        :param msgDescr:
        :return:
        """
        widgetToAdd.setEnabled(False)
        msgTypeText = self.getListOfStrValueAndMeaningFromFieldDescr(msgDescr)
        valueForMsgType = msgTypeText[0]
        widgetToAdd.setCurrentText(str(valueForMsgType))


    def getListOfStrValueAndMeaningFromFieldDescr(self, msgDescr: dict) -> list:
        """
        :param msgDescr:
        :return:
        """
        listOfStrValueAndMeaning = []

        for valueAndMeaning in msgDescr["fieldValuesList"]:
            msgTypeText = str(valueAndMeaning["valueHex"]) + " - " + str(valueAndMeaning["valueMeaning"])
            listOfStrValueAndMeaning += [msgTypeText]

        return listOfStrValueAndMeaning


    def createGroupedFieldsWidget(self, widgetToAdd: QWidget, labelFieldName: str) -> QGroupBox:
        """
        :param widgetToAdd:
        :param labelFieldName:
        :return:
        """
        gridLayGroupedFields = QGridLayout(self)
        gridLayGroupedFields.addWidget(QLabel(labelFieldName), self.groupedFieldsLine, 0)
        gridLayGroupedFields.addWidget(widgetToAdd, self.groupedFieldsLine, 1)

        groupBoxGroupedFields = QGroupBox(self)
        groupBoxGroupedFields.setLayout(gridLayGroupedFields)

        return groupBoxGroupedFields


    def proccessFieldWithRoleIdOrCrc(self, fieldDescr: dict, widgetToAdd: QWidget):
        """
        :param widgetToAdd:
        :param fieldDescr:
        :return:
        """
        self.addCheckBox(fieldDescr)

        if isinstance(widgetToAdd, QLineEdit):
            widgetToAdd.setText('0')
        elif isinstance(widgetToAdd, QSpinBox):
            widgetToAdd.setValue(0)

        widgetToAdd.setEnabled(False)


    def proccessFieldWithRoleLength(self, fieldDescr: dict, widgetToAdd: QWidget):
        """

        :param widgetToAdd:
        :param fieldDescr:
        :return:
        """

        if isinstance(widgetToAdd, QSpinBox):
            widgetToAdd.setEnabled(False)
            self.addCheckBox(fieldDescr)


    def closeGroupedFieldTab(self, tabIndex: int):
        """

        :param tabIndex:
        :return:
        """
        widget = self.tabs.widget(tabIndex)

        if widget is not None:
            groupedWidgetCount = self.widgetInOneGroupCount
            indexOfLatterWidgetToDelete = (len(self.listWidgetTabs) - 1 - groupedWidgetCount * (self.tabs.count() - 2 - tabIndex))
            indexOfFormerWidgetToDelete = indexOfLatterWidgetToDelete - groupedWidgetCount

            for i in range(indexOfLatterWidgetToDelete, indexOfFormerWidgetToDelete, -1):
                self.listWidgetTabs.remove(self.listWidgetTabs[i])

        self.tabs.setCurrentIndex(0)
        self.tabs.removeTab(tabIndex)
        self.tabs.setCurrentIndex(self.tabs.count() - 2)

        self.setResultingMsgString()


    def getLenOfCurrentMsgInBytes(self) -> int:
        """
        :return:
        """

        msg = self.labelResultMsg.text()
        msg = msg.replace('MSG (bin): ', '')
        msg = msg.replace('MSG: ', '')
        msg = msg.replace(' ', '')
        msgLen = len(msg) // 2

        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        excludedLength = self.formatManager.getLengthOfFieldExcludedFromLenCountInMsgType(currentMsgType)
        msgLen -= excludedLength // 8

        if msgLen <= 0:
            msgLen = self.formatManager.getMsgLengthByMsgType(currentMsgType)

        return msgLen


    def removeAllFieldWidgets(self):
        """

        :return:
        """
        self.tabs.hide()
        self.tabs.clear()

        lastTabIndex = self.tabs.count() - 1
        for tabIndex in range(lastTabIndex):
            self.closeGroupedFieldTab(tabIndex)

        for fieldDescrAndWidgets in self.listOfFieldDescrAndWidgets:
            self.removeFieldWidgets(fieldDescrAndWidgets)

        self.listWidgetTabs.clear()
        self.listOfFieldDescrAndWidgets.clear()


    def removeFieldWidgets(self, fieldDescrAndWidgets):
        fieldDescrAndWidgets["labelForFieldTitle"].deleteLater()
        self.gridLayFieldWidgets.removeWidget(fieldDescrAndWidgets["labelForFieldTitle"])

        fieldDescrAndWidgets["widgetForFieldValue"].deleteLater()
        self.gridLayFieldWidgets.removeWidget(fieldDescrAndWidgets["widgetForFieldValue"])

        manualValueCheckBox = fieldDescrAndWidgets["manualValueCheckBox"]
        if manualValueCheckBox:
            manualValueCheckBox.deleteLater()
        self.gridLayFieldWidgets.removeWidget(fieldDescrAndWidgets["manualValueCheckBox"])


    def addCheckBox(self, msgDescr: dict):
        """

        :param msgDescr:
        :return:
        """
        manualValueCheckBox = QCheckBox()
        manualValueCheckBox.setText(_('Manually'))
        manualValueCheckBox.clicked.connect(self.switchEnabledWidget)

        self.listOfFieldDescrAndWidgets[-1]["manualValueCheckBox"] = manualValueCheckBox

        firstFieldTitleInGroup = self.currentMsgDict["firstFieldTitleInGroup"]

        if msgDescr["fieldTitle"] == firstFieldTitleInGroup or self.inProcessOfGroupingFields:
            self.gridLayGroupedFields.addWidget(manualValueCheckBox, self.groupedFieldsLine, 2)
        else:
            self.gridLayFieldWidgets.addWidget(manualValueCheckBox, self.line, 2)


    def getWidgetForEnteringValue(self, msgDescr: dict) -> QWidget:
        if self.formatManager.fieldValuesAreRestricted(msgDescr):
            widgetToReturn = self.createComboBoxWidget(msgDescr)
        elif self.formatManager.fieldLenIsUndef(msgDescr):
            widgetToReturn = self.createLineEditWidget(msgDescr)
        elif int(msgDescr["fieldLength"]) < 32:
            widgetToReturn = self.createSpinBoxWidget(msgDescr)
        else:
            widgetToReturn = self.createLineEditWidget(msgDescr)

        return widgetToReturn


    def createSpinBoxWidget(self, msgDescr: dict) -> QSpinBox:
        """
        :param msgDescr:
        :return:
        """
        widgetToReturn = QSpinBox()
        widgetToReturn.setDisplayIntegerBase(16)

        valueMax = pow(2, int(msgDescr["fieldLength"]))
        valueMax -= 1
        widgetToReturn.setRange(0, valueMax)

        widgetToReturn.valueChanged.connect(self.setResultingMsgString)

        return widgetToReturn


    def createLineEditWidget(self, msgDescr: dict) -> QLineEdit:
        """
        :param msgDescr:
        :return:
        """
        fieldLength = msgDescr["fieldLength"]

        widgetToReturn = QLineEdit()

        if fieldLength != "undef.":
            fieldLengthInSymbols = int(fieldLength) // 4
            widgetToReturn.setText("0" * fieldLengthInSymbols)

        widgetToReturn.textChanged.connect(self.setResultingMsgString)

        hexRegexp = self.getRegexpValidatorFromFieldLength(fieldLength)

        hexValidator = QRegExpValidator(hexRegexp)
        widgetToReturn.setValidator(hexValidator)

        return widgetToReturn


    def getRegexpValidatorFromFieldLength(self, fieldLength):
        if fieldLength == 'undef.':
            hexRegexp = QRegExp("[0-9A-Fa-f]*")
        else:
            fieldLen = str(int(fieldLength) // 4)
            hexRegexp = QRegExp("[0-9A-Fa-f]{," + fieldLen + "}")

        return hexRegexp


    def createComboBoxWidget(self, msgDescr: dict) -> QComboBox:
        """
        :param msgDescr:
        :return:
        """
        widgetToReturn = QComboBox()

        valuesStrList = self.getListOfStrValueAndMeaningFromFieldDescr(msgDescr)

        widgetToReturn.addItems(valuesStrList)

        widgetToReturn.currentTextChanged.connect(self.setResultingMsgString)

        return widgetToReturn


    @pyqtSlot()
    def switchEnabledWidget(self):
        """

        :return:
        """
        for fieldDescrAndWidgets in self.listOfFieldDescrAndWidgets:
            if fieldDescrAndWidgets["manualValueCheckBox"] == QObject.sender(self):
                fieldWidget = fieldDescrAndWidgets["widgetForFieldValue"]
                newState = not fieldWidget.isEnabled()
                fieldWidget.setEnabled(newState)

        self.setResultingMsgString()


    def getListOfEnteredFieldsValues(self) -> list:
        """

        :return:
        """
        listOfEnteredFieldsValues = []

        for fieldDescrAndWidgets in self.listOfFieldDescrAndWidgets:
            fieldValue = self.getFieldValue(fieldDescrAndWidgets)
            listOfEnteredFieldsValues.append(fieldValue)

        groupedValuesList = self.getListOfValuesInGroup()

        msgTypeTitle = self.comboBoxCurrentMsgType.currentText()
        indexOfFirstGroupedField = self.formatManager.getTitleOfFirstFieldInGroupInMsgType(msgTypeTitle)

        if len(groupedValuesList) > 0:
            listOfEnteredFieldsValues[indexOfFirstGroupedField: indexOfFirstGroupedField] = groupedValuesList

        return listOfEnteredFieldsValues


    def getFieldValue(self, fieldDescrAndWidgets: dict) -> str:
        fieldWidget = fieldDescrAndWidgets["widgetForFieldValue"]
        fieldDescr = fieldDescrAndWidgets["fieldDescr"]

        fieldWithRoleIdOrCrc = ((fieldDescr["fieldRole"] == "roleId") or
                                (fieldDescr["fieldRole"] == "roleCrc"))

        if fieldWithRoleIdOrCrc:
            valueEnteredManually = fieldDescrAndWidgets["manualValueCheckBox"].isChecked()
            if not valueEnteredManually:
                fieldValue = 'x'
                return fieldValue

        if isinstance(fieldWidget, QLineEdit):
            fieldValue = self.getFieldValueFromLineEdit(fieldDescrAndWidgets)
        elif isinstance(fieldWidget, QSpinBox):
            fieldValue = self.getFieldValueFromSpinBox(fieldWidget)
        elif isinstance(fieldWidget, QComboBox):
            fieldValue = self.getFieldValueFromComboBox(fieldWidget)
        else:
            fieldValue = ""

        return fieldValue


    def getFieldValueFromLineEdit(self, fieldDescrAndWidgets: dict) -> str:
        fieldWidget = fieldDescrAndWidgets["widgetForFieldValue"]
        fieldDescr = fieldDescrAndWidgets["fieldDescr"]

        if self.formatManager.fieldLenIsUndef(fieldDescr):
            fieldValue = self.getFieldValueForFieldOfUndefLength(fieldWidget)
        else:
            fieldValue = fieldWidget.text()

        return fieldValue


    def getFieldValueFromSpinBox(self, fieldWidget) -> str:
        fieldValue = fieldWidget.value()
        hexFieldValue = hex(fieldValue)
        fieldValue = str(hexFieldValue)
        fieldValue = fieldValue.replace('0x', '')

        return fieldValue


    def getFieldValueFromComboBox(self, fieldWidget) -> str:
        fieldValue = fieldWidget.currentText()
        fieldValue = fieldValue.split(' - ')
        fieldValue = fieldValue[0]

        return fieldValue


    def getFieldValueForFieldOfUndefLength(self, fieldWidget: QWidget) -> str:
        oddNumberOfSymbolsInFieldWidget = (len(fieldWidget.text()) % 2 == 1)

        if oddNumberOfSymbolsInFieldWidget:
            fieldValue = "0"
        else:
            fieldValue = ""
        fieldValue += fieldWidget.text()

        if self.moreThanOneFieldOfUndefLen:
            fieldValue += self.currentMsgDict["separator"]

        return fieldValue


    def msgTypeContainsMoreThanOneFieldOfUndefinedLength(self) -> bool:
        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        self.currentMsgDict = self.formatManager.getInfoForMsgType(currentMsgType)
        fieldDescrsList = self.currentMsgDict["fieldDescrsList"]

        undefLengthFieldsCount = 0

        for fieldDescr in fieldDescrsList:
            if self.formatManager.fieldLenIsUndef(fieldDescr):
                undefLengthFieldsCount += 1

            if undefLengthFieldsCount > 1:
                return True

        return False


    def getListOfValuesInGroup(self) -> list:
        groupedValuesList = []

        for widget in self.listWidgetTabs:
            if isinstance(widget, QLineEdit):
                fieldValue = widget.text()
                groupedValuesList.append(fieldValue)
            elif isinstance(widget, QSpinBox):
                fieldValue = widget.value()
                groupedValuesList.append(fieldValue)
            elif isinstance(widget, QComboBox):
                fieldValue = widget.currentText()
                groupedValuesList.append(fieldValue)

        return groupedValuesList


    @pyqtSlot()
    def saveNamedMsg(self):
        """
        :return:
        """
        msgTitle = self.lineEditMsgTitle.text()
        msgHexStr = self.labelResultMsg.text()

        if self.someUndefFieldContainsOddNumOfHexSymbols():
            self.showErrorMsg(_('Length of field with undefined length does not fit into whole byte'),
                              _('Amount of entered hex symbols should be even'))
            return

        msgHexStr = msgHexStr.replace(_("MSG:"), '')
        msgHexStr = msgHexStr.strip()

        dictForNewNamedMsg = {"msgTitle": msgTitle, "msgHex": msgHexStr}

        managerNamedMsgList = managerNamedMsg.ManagerNamedMsg(self.profileTitle)
        managerNamedMsgList.addNewNamedMsg(dictForNewNamedMsg)

        self.signalNamedMsgAdded.emit(dictForNewNamedMsg)

        self.showSuccessMessageBox(_("Named message \"") + msgTitle + _("\" created!"))


    def idIsSetManually(self) -> bool:
        """
        :return:
        """
        for lineDict in self.listOfFieldDescrAndWidgets:
            if lineDict["manualValueCheckBox"] is not None and \
               lineDict["manualValueCheckBox"].isEnabled() and \
               lineDict["manualValueCheckBox"].isChecked() and \
               lineDict["fieldDescr"]["fieldRole"] == "roleId":
                return True

        return False


    def someUndefFieldContainsOddNumOfHexSymbols(self) -> bool:
        """
        :return:
        """
        listOfUndefFieldsStr = self.getListOfStrForUndefLenFields()

        fieldContainsOddNumOfHexSymbols = False

        for undefFieldStr in listOfUndefFieldsStr:
            if len(undefFieldStr) % 2 == 1:
                fieldContainsOddNumOfHexSymbols = True

        return fieldContainsOddNumOfHexSymbols


    def getListOfStrForUndefLenFields(self) -> list:
        """
        :return:
        """
        listOfUndefStr = []

        msgHexStr = self.labelResultMsg.text()
        msgHexStr = msgHexStr.replace(_("MSG:"), '')
        msgHexStr = msgHexStr.strip()

        listOfStr = msgHexStr.split(' ')

        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        msgCreator = handlerMsgCreator.HandlerMsgCreator(self.profileTitle)
        msgCreator.setMsgType(currentMsgType)

        for i in range(len(listOfStr)):
            adjustedIndex = msgCreator.adjustIndexForMsgWithGroupedFieldsInMsgType(i)
            field = self.currentMsgDict["fieldDescrsList"][adjustedIndex]

            if field["fieldLength"] == 'undef.':
                listOfUndefStr.append(listOfStr[i])

        return listOfUndefStr


    @pyqtSlot()
    def addNewTab(self):
        """
        Ignore for now, not tested and ugly
        :return:
        """

        nextTabIndex = self.tabs.currentIndex() + 1
        currentTabIsTubWithPlusForAddingNewTabs = (self.tabs.currentIndex() > 0 and nextTabIndex == self.tabs.count())

        if currentTabIsTubWithPlusForAddingNewTabs:
            indexBefore = self.tabs.currentIndex()

            gridLayForGroupedFields = self.addGridLayForGroupedFields()

            self.prepareTabs(indexBefore)

            groupedFieldsLine = 0

            for index, widgetGrouped in enumerate(self.listWidgetTabs):
                if isinstance(widgetGrouped, QGridLayout) or isinstance(widgetGrouped, QGroupBox):
                    continue

                widget = self.getGroupedWidget(groupedFieldsLine, widgetGrouped)
                self.listWidgetTabs.append(widget)

                widgetColumn = self.getWidgetColumnForGroupedWidgets(widgetGrouped)

                gridLayForGroupedFields.addWidget(widget, groupedFieldsLine, widgetColumn)

                if isinstance(widgetGrouped, QCheckBox):
                    groupedFieldsLine += 1
                else:
                    widgetCount = len(self.listWidgetTabs[0].children())
                    nextWidgetIndex = index + 1
                    lastWidgetIndex = widgetCount - 1

                    if nextWidgetIndex >= lastWidgetIndex or isinstance(self.listWidgetTabs[0].children()[index + 1], QCheckBox):
                        groupedFieldsLine += 1

            self.setResultingMsgString()


    def prepareTabs(self, indexBefore):
        self.tabs.addTab(QWidget(), '+')
        self.tabs.removeTab(indexBefore)
        tabBar = self.tabs.findChild(QTabBar)
        tabBar.setTabButton(self.tabs.count() - 1, QTabBar.RightSide, None)
        tabBar.setTabButton(self.tabs.count() - 1, QTabBar.LeftSide, None)


    def addGridLayForGroupedFields(self):
        groupBoxGroupedFields = QGroupBox(self)

        gridLayForGroupedFields = QGridLayout(self)
        groupBoxGroupedFields.setLayout(gridLayForGroupedFields)

        self.listWidgetTabs.append(groupBoxGroupedFields)
        self.tabs.addTab(groupBoxGroupedFields, _('Group'))

        return gridLayForGroupedFields


    def getGroupedWidget(self, groupedFieldsLine, widgetGrouped):
        if isinstance(widgetGrouped, QLabel):
            widget = QLabel(widgetGrouped.text())
        elif isinstance(widgetGrouped, QCheckBox):
            widget = QCheckBox()
            widget.setText(_('Manually'))
            widget.clicked.connect(self.switchEnabledWidget)
        else:
            msgTypeTitle = self.comboBoxCurrentMsgType.currentText()
            indexOfFirstGroupedField = self.formatManager.getIndexOfFirstFieldInGroupInMsgType(msgTypeTitle)

            currentFieldDescrsList = self.currentMsgDict["fieldDescrsList"]
            widget = self.getWidgetForEnteringValue(currentFieldDescrsList[indexOfFirstGroupedField +
                                                                           groupedFieldsLine])

        return widget


    def getWidgetColumnForGroupedWidgets(self, widgetGrouped) -> int:
        if isinstance(widgetGrouped, QLabel):
            widgetPosition = 0
        elif isinstance(widgetGrouped, QCheckBox):
            widgetPosition = 2
        else:
            widgetPosition = 1

        return widgetPosition
