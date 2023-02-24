import gettext

from PyQt5.Qt import Qt
from PyQt5.QtCore import QObject, QRegExp, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QCheckBox, QComboBox, QGridLayout, QGroupBox
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QSpinBox
from PyQt5.QtWidgets import QTabBar, QTabWidget, QVBoxLayout, QWidget

import src.handlers.handlerMsgCreator as handlerMsgCreator
import src.handlers.handlerString as handlerString
import src.managers.managerNamedRegexp as managerNamedRegexp
import src.ui.windows.windowProfiledWindow as windowProfiledWindow

_ = gettext.gettext


class WindowNamedRegexpEditor(windowProfiledWindow.WindowProfiledWindow):
    signalNamedRegexpAdded = pyqtSignal(str, str)

    def __init__(self, profileTitle: str, parent=None):
        super().__init__(profileTitle, parent)
        self.inProcessOfGroupingFields = False

        self.line = 0
        self.groupedFieldsLine = 0
        self.widgetInOneGroupCount = 0

        self.listWidgetTabs = []

        self.fieldDescrAndWidgetsDict = {"fieldDescr": dict(), "widgetForFieldValue": QWidget(),
                                         "anyValueCheckBox": QCheckBox()}
        self.listOfFieldDescrAndWidgets = []

        self.currentMsgDescrList = []

        self.allGroupedFieldValuesAsAnyValueFlag = False

        self.msgCreator = handlerMsgCreator.HandlerMsgCreator(profileTitle)

        self.initUI()


    def initUI(self) -> None:
        self.setWindowProperties()

        self.vLayoutPrincipal = QVBoxLayout(self)

        self.addWidgetsForEnteringRegexpName()
        self.addWidgetsForChoosingMsgType()

        self.gridLayFieldWidgets = QGridLayout(self)
        self.groupBoxFields = self.addGroupBoxForFields()

        self.labelResultMsg = self.addLabelWithResultMsg()

        self.addWidgetsForGroupedFields()

        self.addButtonsSaveAndClose()

        self.vLayoutPrincipal.addStretch(10)

        self.show()


    def setWindowProperties(self) -> None:
        title = _('Named Regexp Editor')
        self.setWindowTitle(title)

        self.setModal(True)
        self.setFocusPolicy(Qt.StrongFocus)


    def addWidgetsForGroupedFields(self) -> None:
        self.tabs = self.addTabWidgetForGroupedFields()

        self.groupBoxGroupedFields = self.addGroupBoxForGroupedFields()

        self.checkBoxGroupedFieldsAnyValue = self.addCheckBoxGroupedFieldsAnyValue()

        self.labelGroupedFieldsAnyValue = QLabel(_('Any value in grouped fields'))
        self.labelGroupedFieldsAnyValue.hide()


    def addButtonsSaveAndClose(self) -> None:
        hLayButtonsSaveClose = QHBoxLayout(self)

        self.buttonSave.clicked.connect(self.saveNamedRegexp)
        hLayButtonsSaveClose.addWidget(self.buttonSave)

        hLayButtonsSaveClose.addWidget(self.buttonClose)

        self.vLayoutPrincipal.addLayout(hLayButtonsSaveClose)


    def addGroupBoxForGroupedFields(self) -> QGroupBox:
        gridLayGroupedFields = QGridLayout(self)

        groupBoxGroupedFields = QGroupBox(self)

        groupBoxGroupedFields.setLayout(gridLayGroupedFields)
        groupBoxGroupedFields.hide()

        return groupBoxGroupedFields


    def addCheckBoxGroupedFieldsAnyValue(self) -> QCheckBox:
        checkBoxGroupedFieldsAnyValue = QCheckBox()

        checkBoxGroupedFieldsAnyValue.hide()
        checkBoxGroupedFieldsAnyValue.clicked.connect(self.setAllGroupedFieldValuesAsAnyValueFlag)

        return checkBoxGroupedFieldsAnyValue


    def addTabWidgetForGroupedFields(self) -> QTabWidget:
        tabs = QTabWidget()
        tabs.hide()
        self.vLayoutPrincipal.addWidget(tabs)

        return tabs


    def addComboBoxWithCurrentMsgType(self) -> QComboBox:
        comboBoxCurrentMsgType = QComboBox(self)
        listMsgTypes = self.formatManager.getListOfAllMsgTypeTitles()

        comboBoxCurrentMsgType.addItem('')
        comboBoxCurrentMsgType.addItems(listMsgTypes)
        comboBoxCurrentMsgType.setCurrentIndex(0)
        comboBoxCurrentMsgType.currentTextChanged.connect(self.updateFormForMsgTypeSelected)

        return comboBoxCurrentMsgType


    def addGroupBoxForFields(self) -> QGroupBox:
        groupBoxFields = QGroupBox(self)
        groupBoxFields.setLayout(self.gridLayFieldWidgets)
        groupBoxFields.setTitle(_('MSG fields:'))
        groupBoxFields.hide()

        self.vLayoutPrincipal.addWidget(groupBoxFields)

        return groupBoxFields


    def addLabelWithResultMsg(self) -> QLabel:
        labelResultMsg = QLabel(_('MSG: '))
        labelResultMsg.setStyleSheet('QLabel {background-color : rgba(200, 200, 200); }')
        labelResultMsg.setWordWrap(True)

        self.vLayoutPrincipal.addWidget(labelResultMsg)

        return labelResultMsg


    def addWidgetsForEnteringRegexpName(self) -> QHBoxLayout:
        hLayEnterRegexpName = QHBoxLayout(self)

        self.labelEnterRegexpName = QLabel(_('Title'))
        self.lineEditRegexpName = QLineEdit(self)

        hLayEnterRegexpName.addWidget(self.labelEnterRegexpName)
        hLayEnterRegexpName.addWidget(self.lineEditRegexpName)

        self.vLayoutPrincipal.addLayout(hLayEnterRegexpName)

        return hLayEnterRegexpName


    def addWidgetsForChoosingMsgType(self) -> None:
        hLayChooseMsgType = QHBoxLayout(self)
        labelChooseMsgType = QLabel(_('Select MSG type'))

        hLayChooseMsgType.addWidget(labelChooseMsgType)

        self.comboBoxCurrentMsgType = self.addComboBoxWithCurrentMsgType()
        hLayChooseMsgType.addWidget(self.comboBoxCurrentMsgType)

        self.vLayoutPrincipal.addLayout(hLayChooseMsgType)


    def setAllGroupedFieldValuesAsAnyValueFlag(self) -> None:
        self.allGroupedFieldValuesAsAnyValueFlag = not self.allGroupedFieldValuesAsAnyValueFlag
        self.updateCreatedMsgLabel()


    @pyqtSlot()
    def updateFormForMsgTypeSelected(self) -> None:
        """
        Creates and adds on window widgets according to message type structure for further message editing.
        Creates list of dictionaries that store (for each field): a field descriptor, a label for field title,
        a widget for field value, a check-box to mark field as any value, and an any value label
        :return:
        """
        self.removeAllFieldWidgets()

        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        if currentMsgType == '':
            self.adjustSize()
            return

        self.prepareToSwitchToNewMsgType()

        self.addWidgetsAndRenewDataForSelectedMsgType()

        self.markAllFieldOfUndefLenAsAnyValue()

        self.setResultingMsgString()

        self.adjustSize()


    def addWidgetsAndRenewDataForSelectedMsgType(self) -> None:
        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        fieldDescrsList = self.formatManager.getFieldDescrsListForMsgType(currentMsgType)

        for fieldDescr in fieldDescrsList:
            self.processFieldDescr(fieldDescr)


    def processFieldDescr(self, fieldDescr) -> None:
        fieldDescrAndWidgetsDict = self.getFieldDescrAndWidgetsDict(fieldDescr)

        self.proccessFieldsWithSpecialRoles(fieldDescrAndWidgetsDict)
        self.listOfFieldDescrAndWidgets.append(fieldDescrAndWidgetsDict)
        self.line += 1


    def prepareToSwitchToNewMsgType(self) -> None:
        self.checkBoxGroupedFieldsAnyValue.hide()
        self.labelGroupedFieldsAnyValue.hide()

        self.groupBoxFields.show()

        self.line = 0
        self.groupedFieldsLine = 0
        self.inProcessOfGroupingFields = False
        self.widgetInOneGroupCount = 0


    def getFieldDescrAndWidgetsDict(self, fieldDescr: dict) -> dict:
        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        currentMsgDict = self.formatManager.getInfoForMsgType(currentMsgType)
        firstFieldTitleInGroup = currentMsgDict["firstFieldTitleInGroup"]

        if fieldDescr["fieldTitle"] == firstFieldTitleInGroup:
            fieldDescrAndWidgetsDict = self.proccessFirstFieldInGroup(fieldDescr)
        elif self.inProcessOfGroupingFields:
            fieldDescrAndWidgetsDict = self.proccessOtherFieldsInGroup(fieldDescr)
        else:
            fieldDescrAndWidgetsDict = self.proccesNoneGroupedField(fieldDescr)

        return fieldDescrAndWidgetsDict


    def markAllFieldOfUndefLenAsAnyValue(self) -> None:
        for fieldDescrAndWidgets in self.listOfFieldDescrAndWidgets:
            fieldDescr = fieldDescrAndWidgets["fieldDescr"]

            if fieldDescr["fieldLength"] == "undef.":
                anyValueCheckBox = fieldDescrAndWidgets["anyValueCheckBox"]
                anyValueCheckBox.setChecked(True)


    def proccessFieldsWithSpecialRoles(self, fieldDescrAndWidgetsDict: dict) -> None:
        fieldDescr = fieldDescrAndWidgetsDict["fieldDescr"]

        if self.fieldRoleIsLength(fieldDescr):
            self.proccessFieldWithRoleLength(fieldDescrAndWidgetsDict)
        elif self.fieldRoleIsId(fieldDescr) or self.fieldRoleIsCrc(fieldDescr):
            self.proccessFieldWithRoleIdOrCrc(fieldDescrAndWidgetsDict)
        elif self.fieldRoleIsType(fieldDescr):
            self.proccessFieldWithRoleType(fieldDescrAndWidgetsDict)


    def proccesNoneGroupedField(self, fieldDescr: dict) -> dict:
        fieldDescrAndWidgetsDict = self.getFieldDescrAndWidgetDict(fieldDescr)

        labelForFieldTitle = fieldDescrAndWidgetsDict["labelForFieldTitle"]
        widgetForFieldValue = fieldDescrAndWidgetsDict["widgetForFieldValue"]
        anyValueCheckBox = fieldDescrAndWidgetsDict["anyValueCheckBox"]

        self.gridLayFieldWidgets.addWidget(labelForFieldTitle, self.line, 0)
        self.gridLayFieldWidgets.addWidget(widgetForFieldValue, self.line, 1)
        self.gridLayFieldWidgets.addWidget(anyValueCheckBox, self.line, 2)

        return fieldDescrAndWidgetsDict


    def proccessOtherFieldsInGroup(self, fieldDescr: dict) -> dict:
        self.addLabelForFieldTitle(fieldDescr)
        self.addWidgetForFieldValue(fieldDescr)
        self.addAnyValueCheckBox(fieldDescr)

        self.groupedFieldsLine += 1

        currentMsgType = self.comboBoxCurrentMsgType.currentText()

        fieldTitle = fieldDescr["fieldTitle"]
        thisIsLastFieldInGroupInMsgType = self.formatManager.fieldIsLastFieldInGroupInMsgType(fieldTitle, currentMsgType)

        if thisIsLastFieldInGroupInMsgType:
            self.proccessWidgetsForLastFieldInGroup()

        fieldDescrAndWidgetsDict = self.getFieldDescrAndWidgetDict(fieldDescr)

        return fieldDescrAndWidgetsDict


    def addWidgetForFieldValue(self, fieldDescr: dict) -> None:
        fieldDescrAndWidgetsDict = self.getFieldDescrAndWidgetDict(fieldDescr)

        widgetForFieldValue = fieldDescrAndWidgetsDict["widgetForFieldValue"]
        self.listWidgetTabs[0].children()[0].addWidget(widgetForFieldValue, self.groupedFieldsLine, 1)
        self.listWidgetTabs.append(widgetForFieldValue)


    def addLabelForFieldTitle(self, fieldDescr: dict) -> None:
        fieldDescrAndWidgetsDict = self.getFieldDescrAndWidgetDict(fieldDescr)

        labelForFieldTitle = fieldDescrAndWidgetsDict["labelForFieldTitle"]
        self.listWidgetTabs[0].children()[0].addWidget(labelForFieldTitle, self.groupedFieldsLine, 0)
        self.listWidgetTabs.append(labelForFieldTitle)


    def addAnyValueCheckBox(self, fieldDescr: dict) -> None:
        fieldDescrAndWidgetsDict = self.getFieldDescrAndWidgetDict(fieldDescr)

        anyValueCheckBox = fieldDescrAndWidgetsDict["anyValueCheckBox"]
        self.listWidgetTabs[0].children()[0].addWidget(anyValueCheckBox, self.groupedFieldsLine, 2)
        self.listWidgetTabs.append(anyValueCheckBox)


    def proccessWidgetsForLastFieldInGroup(self) -> None:
        self.inProcessOfGroupingFields = False
        self.widgetInOneGroupCount = len(self.listWidgetTabs)

        self.gridLayFieldWidgets.addWidget(self.checkBoxGroupedFieldsAnyValue, self.line, 0)
        self.gridLayFieldWidgets.addWidget(self.labelGroupedFieldsAnyValue, self.line, 1)

        self.checkBoxGroupedFieldsAnyValue.show()
        self.labelGroupedFieldsAnyValue.show()


    def getFieldDescrAndWidgetDict(self, fieldDescr: dict) -> dict:
        fieldDescrAndWidgetsDict = {"labelForFieldTitle":  QLabel(),
                                    "fieldDescr":          dict(),
                                    "widgetForFieldValue": QWidget(),
                                    "anyValueCheckBox":    QCheckBox(),
                                    "anyValueLabel":       QLabel()}

        fieldDescrAndWidgetsDict["fieldDescr"] = fieldDescr

        fieldTitle = fieldDescr["fieldTitle"] + " (" + str(fieldDescr["fieldLength"]) + ")"
        fieldDescrAndWidgetsDict["labelForFieldTitle"] = QLabel(fieldTitle)

        widgetForFieldValue = self.getWidgetForEnteringValue(fieldDescr)
        fieldDescrAndWidgetsDict["widgetForFieldValue"] = widgetForFieldValue

        anyValueCheckBox = self.getAnyValueCheckBox(fieldDescr)
        fieldDescrAndWidgetsDict["anyValueCheckBox"] = anyValueCheckBox

        return fieldDescrAndWidgetsDict


    def proccessFirstFieldInGroup(self, fieldDescr: dict) -> dict:
        self.inProcessOfGroupingFields = True
        self.gridLayFieldWidgets.addWidget(self.tabs, self.line, 0, 1, 3)

        fieldDescrAndWidgetsDict = self.getFieldDescrAndWidgetDict(fieldDescr)
        groupBoxGroupedFields = self.getGroupBoxWithGroupedFields(fieldDescr)
        self.setUpFirstTab(groupBoxGroupedFields)

        return fieldDescrAndWidgetsDict


    def getGroupBoxWithGroupedFields(self, fieldDescr: dict) -> QGroupBox:
        groupBoxGroupedFields = QGroupBox(self)
        self.listWidgetTabs.append(groupBoxGroupedFields)

        gridLayGroupedFields = QGridLayout(self)
        groupBoxGroupedFields.setLayout(gridLayGroupedFields)

        fieldDescrAndWidgetsDict = self.getFieldDescrAndWidgetDict(fieldDescr)

        labelForFieldTitle = fieldDescrAndWidgetsDict["labelForFieldTitle"]
        gridLayGroupedFields.addWidget(labelForFieldTitle, self.groupedFieldsLine, 0)
        self.listWidgetTabs.append(labelForFieldTitle)

        widgetForFieldValue = fieldDescrAndWidgetsDict["widgetForFieldValue"]
        gridLayGroupedFields.addWidget(widgetForFieldValue, self.groupedFieldsLine, 1)
        self.listWidgetTabs.append(widgetForFieldValue)

        anyValueCheckBox = fieldDescrAndWidgetsDict["anyValueCheckBox"]
        gridLayGroupedFields.addWidget(anyValueCheckBox, self.groupedFieldsLine, 2)
        self.listWidgetTabs.append(anyValueCheckBox)

        self.groupedFieldsLine += 1

        return groupBoxGroupedFields


    def setUpFirstTab(self, groupBoxGroupedFields: QGroupBox) -> None:
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


    def setResultingMsgString(self) -> None:
        """
        :return:
        """
        listOfInitialHexFieldValues = self.getListOfEnteredFieldsValues()

        strHandler = handlerString.HandlerString()
        listOfInitialBinFieldValues = strHandler.getListOfBinValuesFromListOfHexValues(listOfInitialHexFieldValues)
        self.msgCreator.setListOfFieldValuesFromList(listOfInitialBinFieldValues)

        currentMsgTypeTitle = self.comboBoxCurrentMsgType.currentText()
        exampleMsg = self.msgCreator.getMsgFromListOfPreviouslySetBinFieldsValuesInMsgType(currentMsgTypeTitle)

        self.labelResultMsg.setText(_('MSG: ') + exampleMsg)


    def proccessFieldWithRoleType(self, fieldDescrAndWidgetsDict: dict) -> None:
        """
        :param fieldDescrAndWidgetsDict:
        :return:
        """
        widgetForFieldValue = fieldDescrAndWidgetsDict["widgetForFieldValue"]
        fieldDescr = fieldDescrAndWidgetsDict["fieldDescr"]

        widgetForFieldValue.setEnabled(False)

        typeStr = fieldDescr["fieldValuesList"][0]["valueHex"] + " - " + fieldDescr["fieldValuesList"][0]["valueMeaning"]

        widgetForFieldValue.setCurrentText(typeStr)


    def createGroupedFieldsWidget(self, widgetToAdd: QWidget, labelFieldName: QLabel) -> QGroupBox:
        """
        :param widgetToAdd:
        :param labelFieldName:
        :return:
        """
        gridLayGroupedFields = QGridLayout(self)
        gridLayGroupedFields.addWidget(labelFieldName, self.groupedFieldsLine, 0)
        gridLayGroupedFields.addWidget(widgetToAdd, self.groupedFieldsLine, 1)

        groupBoxGroupedFields = QGroupBox(self)
        groupBoxGroupedFields.setLayout(gridLayGroupedFields)

        return groupBoxGroupedFields


    def proccessFieldWithRoleIdOrCrc(self, fieldDescrAndWidgetsDict: dict):
        """
        :param fieldDescrAndWidgetsDict:
        :return:
        """
        widgetForFieldValue = fieldDescrAndWidgetsDict["widgetForFieldValue"]

        if isinstance(widgetForFieldValue, QLineEdit):
            widgetForFieldValue.setText('00')
        elif isinstance(widgetForFieldValue, QSpinBox):
            widgetForFieldValue.setValue(0)

        widgetForFieldValue.setEnabled(False)


    def proccessFieldWithRoleLength(self, fieldDescrAndWidgetsDict: dict):
        """
        :param fieldDescrAndWidgetsDict
        :return:
        """

        widgetForFieldValue = fieldDescrAndWidgetsDict["widgetForFieldValue"]

        msgLength = self.getLenOfCurrentMsgInBytes()
        if isinstance(widgetForFieldValue, QLineEdit):
            widgetForFieldValue.setText(str(msgLength))
        elif isinstance(widgetForFieldValue, QSpinBox):
            widgetForFieldValue.setValue(msgLength)
            widgetForFieldValue.setEnabled(False)


    def closeGroupedFieldTab(self, tabIndex: int):
        """
        :param tabIndex:
        :return:
        """

        widget = self.tabs.widget(tabIndex)

        for childWidget in widget.children():
            if not isinstance(childWidget, QGridLayout):
                for line in self.listOfFieldDescrAndWidgets:
                    if line["anyValueCheckBox"] == childWidget:
                        self.listOfFieldDescrAndWidgets.remove(line)

                self.listWidgetTabs.remove(childWidget)

        self.tabs.setCurrentIndex(0)
        self.tabs.removeTab(tabIndex)
        self.tabs.setCurrentIndex(self.tabs.count() - 2)

        self.updateCreatedMsgLabel()


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


    def removeAllFieldWidgets(self) -> None:
        """
        :return:
        """
        self.tabs.hide()
        self.tabs.clear()

        for i in range(self.tabs.count()-1):
            self.closeGroupedFieldTab(i)

        for fieldDescrAndWidgets in self.listOfFieldDescrAndWidgets:
            fieldDescrAndWidgets["anyValueCheckBox"].deleteLater()
            fieldDescrAndWidgets["labelForFieldTitle"].deleteLater()

            widget = fieldDescrAndWidgets["widgetForFieldValue"]

            widget.hide()
            self.gridLayFieldWidgets.removeWidget(widget)
            widget.deleteLater()

        self.listOfFieldDescrAndWidgets.clear()
        self.listWidgetTabs.clear()


    def getAnyValueCheckBox(self, fieldDescr: dict) -> QCheckBox:
        """
        :param fieldDescr:
        :return:
        """
        anyValueCheckBox = QCheckBox()
        anyValueCheckBox.setText(_('Any value'))
        anyValueCheckBox.clicked.connect(self.onClickCheckBoxAnyValue)

        if self.fieldRoleIsType(fieldDescr):
            anyValueCheckBox.setEnabled(False)
        elif self.fieldRoleIsId(fieldDescr) or self.fieldRoleIsCrc(fieldDescr):
            anyValueCheckBox.setChecked(True)
            anyValueCheckBox.setEnabled(False)

        return anyValueCheckBox


    def getWidgetForEnteringValue(self, fieldDescr: dict) -> QWidget:
        """
        :param fieldDescr:
        :return:
        """

        if self.fieldValuesAreRestricted(fieldDescr):
            widgetToReturn = self.createComboBoxWidget(fieldDescr)
        elif self.fieldLenIsUndef(fieldDescr):
            widgetToReturn = self.createLineEditWidget(fieldDescr)
        elif int(fieldDescr["fieldLength"]) <= 32:
            widgetToReturn = self.createSpinBoxWidget(fieldDescr)
        else:
            widgetToReturn = self.createLineEditWidget(fieldDescr)

        return widgetToReturn


    def createSpinBoxWidget(self, fieldDescr: dict) -> QSpinBox:
        """
        :param fieldDescr:
        :return:
        """
        widgetToReturn = QSpinBox()
        widgetToReturn.setDisplayIntegerBase(16)

        valueMax = pow(2, int(fieldDescr["fieldLength"]))
        valueMax -= 1

        widgetToReturn.setRange(0, valueMax)
        widgetToReturn.setPrefix('0x')
        widgetToReturn.valueChanged.connect(self.updateCreatedMsgLabel)

        return widgetToReturn


    def createLineEditWidget(self, fieldDescr: dict) -> QLineEdit:
        """
        :param fieldDescr:
        :return:
        """
        widgetToReturn = QLineEdit()
        widgetToReturn.textChanged.connect(self.updateCreatedMsgLabel)

        if fieldDescr["fieldLength"] == 'undef.':
            hexRegexp = QRegExp("[0-9A-Fa-f]*")
        else:
            fieldLen = str(int(fieldDescr["fieldLength"]) // 4)
            hexRegexp = QRegExp("[0-9A-Fa-f]{," + fieldLen + "}")

        hexValidator = QRegExpValidator(hexRegexp)
        widgetToReturn.setValidator(hexValidator)

        return widgetToReturn


    def createComboBoxWidget(self, fieldDescr: dict) -> QComboBox:
        """
        :param fieldDescr:
        :return:
        """
        widgetToReturn = QComboBox()

        for valueDescr in fieldDescr["fieldValuesList"]:
            widgetToReturn.addItem(valueDescr["valueHex"] + " - " + valueDescr["valueMeaning"])

        widgetToReturn.currentTextChanged.connect(self.updateCreatedMsgLabel)

        return widgetToReturn


    def fieldLenIsUndef(self, fieldDescr: dict) -> bool:
        """
        :param fieldDescr:
        :return:
        """
        if fieldDescr["fieldLength"] == 'undef.':
            return True
        else:
            return False


    def fieldValuesAreRestricted(self, fieldDescr: dict) -> bool:
        """
        :param fieldDescr:
        :return:
        """
        if fieldDescr["fieldLength"] != 'undef.' and len(fieldDescr["fieldValuesList"]) > 0:
            return True
        else:
            return False


    def fieldRoleIsLength(self, fieldDescr: dict) -> bool:
        """
        :param fieldDescr:
        :return:
        """
        if fieldDescr["fieldRole"] == 'roleLength':
            return True
        else:
            return False


    def fieldRoleIsId(self, fieldDescr: dict) -> bool:
        """
        :param fieldDescr:
        :return:
        """
        if fieldDescr["fieldRole"] == 'roleId':
            return True
        else:
            return False


    def fieldRoleIsCrc(self, fieldDescr: dict) -> bool:
        """
        :param fieldDescr:
        :return:
        """
        if fieldDescr["fieldRole"] == 'roleCrc':
            return True
        else:
            return False


    def fieldRoleIsType(self, fieldDescr: dict) -> bool:
        """
        :param fieldDescr:
        :return:
        """
        if fieldDescr["fieldRole"] == 'roleType':
            return True
        else:
            return False


    @pyqtSlot()
    def onClickCheckBoxAnyValue(self) -> None:
        for fieldDescrAndWidgets in self.listOfFieldDescrAndWidgets:
            fieldAnyValueCheckBox = fieldDescrAndWidgets["anyValueCheckBox"]

            if fieldAnyValueCheckBox == QObject.sender(self):
                self.switchFieldWidgetState(fieldDescrAndWidgets)
                self.setFieldWidgetText(fieldDescrAndWidgets)

        self.setResultingMsgString()


    def switchFieldWidgetState(self, fieldDescrAndWidgets: dict) -> None:
        fieldWidget = fieldDescrAndWidgets["widgetForFieldValue"]
        fieldAnyValueCheckBox = fieldDescrAndWidgets["anyValueCheckBox"]

        if fieldAnyValueCheckBox.isChecked():
            fieldWidget.setEnabled(False)
        else:
            fieldWidget.setEnabled(True)


    def setFieldWidgetText(self, fieldDescrAndWidgets: dict) -> None:
        fieldWidget = fieldDescrAndWidgets["widgetForFieldValue"]
        fieldAnyValueCheckBox = fieldDescrAndWidgets["anyValueCheckBox"]

        if isinstance(fieldWidget, QLineEdit):
            if fieldAnyValueCheckBox.isChecked():
                fieldWidget.setText('([0-1]{8})*')
            else:
                fieldWidget.setText('')


    @pyqtSlot()
    def updateCreatedMsgLabel(self) -> None:
        """
        :return:
        """
        listOfFieldsValues = self.getListOfEnteredFieldsValues()

        currentMsgType = self.comboBoxCurrentMsgType.currentText()

        self.msgCreator.setListOfFieldValuesFromList(listOfFieldsValues)
        strExampleMsg = self.msgCreator.getMsgFromListOfPreviouslySetHexFieldValuesInMsgType(currentMsgType)

        if self.someDataFieldsAreStillInBinMode():
            self.setExampleMsgInBinMode()
        else:
            self.labelResultMsg.setText(_('MSG: ') + strExampleMsg)


    def setExampleMsgInBinMode(self) -> None:
        listOfPaddedValues = self.getListOfBinPaddedValues()

        if self.allGroupedFieldValuesAsAnyValueFlag:
            listOfPaddedValues = self.getListOfPaddedValuesWithRegexpForAllGroupedFields(listOfPaddedValues)
            listOfPaddedValues = self.setFieldWithRoleLengthAsAnyValueInListOfPaddedFieldValues(listOfPaddedValues)

        for fieldDescrAndWidgets in self.listOfFieldDescrAndWidgets:
            fieldDescr = fieldDescrAndWidgets["fieldDescr"]

            if len(fieldDescr) < 2:
                break

            anyValueFlagOn = fieldDescrAndWidgets["anyValueCheckBox"].isChecked()

            if fieldDescr["fieldLength"] == 'undef.' and anyValueFlagOn:
                listOfPaddedValues = self.setFieldWithRoleLengthAsAnyValueInListOfPaddedFieldValues(listOfPaddedValues)
                break

        binStrExampleMsg = ' '.join(listOfPaddedValues)
        self.labelResultMsg.setText(_('MSG (bin): ') + binStrExampleMsg)


    def setFieldWithRoleLengthAsAnyValueInListOfPaddedFieldValues(self, listOfPaddedValues: list) -> list:
        """
        :param listOfPaddedValues:
        :return:
        """
        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        indexOfFieldWithRoleLength = self.formatManager.getIndexOfFieldWithRoleLengthInMsgType(currentMsgType)
        lengthOfFieldWithRoleLength = self.formatManager.getLengthOfFieldWithRoleLengthInMsgType(currentMsgType)

        listOfPaddedValues[indexOfFieldWithRoleLength] = 'x' * lengthOfFieldWithRoleLength

        return listOfPaddedValues


    def getListOfBinPaddedValues(self) -> list:
        """
        :return:
        """
        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        binStrSepar = self.formatManager.getBinSeparatorForMsgType(currentMsgType)

        listOfFieldsValues = self.getListOfEnteredFieldsValues()

        self.msgCreator.setListOfFieldValuesFromList(listOfFieldsValues)
        self.msgCreator.setMsgType(currentMsgType)
        listOfPaddedValues = self.msgCreator.getListOfPaddedBinFieldsValues(listOfFieldsValues)
        listOfPaddedValuesLen = len(listOfPaddedValues)

        for index in range(listOfPaddedValuesLen):
            adjustedIndex = self.msgCreator.adjustIndexForMsgWithGroupedFieldsInMsgType(index)

            fieldDescrAndWidgets = self.listOfFieldDescrAndWidgets[index]
            if fieldDescrAndWidgets["anyValueCheckBox"].isChecked():
                if self.msgCreator.fieldLengthIsUndef(adjustedIndex):
                    listOfPaddedValues[index] = '([0-1]{8})*' + binStrSepar
                else:
                    listOfPaddedValues[index] = 'x' * (len(listOfPaddedValues[index].strip()))

        return listOfPaddedValues


    def getListOfPaddedValuesWithRegexpForAllGroupedFields(self, listOfPaddedValues: list) -> list:
        """
        :param listOfPaddedValues:
        :return:
        """
        listOfPaddedValuesLen = len(listOfPaddedValues)
        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        firstGroupedValueIndex = self.formatManager.getIndexOfFirstFieldInGroupInMsgType(currentMsgType)

        lastGroupedValueIndex = listOfPaddedValuesLen - self.formatManager.getCountOfTaleFieldsInMsgType(currentMsgType)

        groupedFieldsRegexp = '(' + self.msgCreator.getBinRegexpOfGroupedField() + ')*'

        newListOfPaddedValues = listOfPaddedValues[:firstGroupedValueIndex]

        newListOfPaddedValues.append(groupedFieldsRegexp)
        newListOfPaddedValues.extend(listOfPaddedValues[lastGroupedValueIndex:])

        listOfPaddedValues = newListOfPaddedValues

        return listOfPaddedValues


    def someDataFieldsAreStillInBinMode(self) -> bool:
        """
        :return:
        """

        for descrAndWidgets in self.listOfFieldDescrAndWidgets:
            fieldDescr = descrAndWidgets["fieldDescr"]

            if self.fieldRoleIsId(fieldDescr):
                return False
            elif self.fieldRoleIsType(fieldDescr):
                return False
            elif self.fieldRoleIsLength(fieldDescr):
                return False
            elif self.fieldRoleIsCrc(fieldDescr):
                return False
            elif descrAndWidgets["anyValueCheckBox"].isChecked():
                return True

        return False


    def getListOfEnteredFieldsValues(self) -> list:
        """
        :return:
        """
        listOfEnteredFieldsValues = self.getListEnteredNoneGroupedValues()
        listOfEnteredFieldsValues = self.setLengthValueForFieldWithRoleLength(listOfEnteredFieldsValues)

        groupedValuesList = self.getGroupedValuesList()

        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        index = self.formatManager.getIndexOfFirstFieldInGroupInMsgType(currentMsgType)

        if len(groupedValuesList) > 0:
            listOfEnteredFieldsValues[index: index] = groupedValuesList

        return listOfEnteredFieldsValues


    def getListEnteredNoneGroupedValues(self) -> list:
        """
        :return:
        """
        listOfEnteredFieldsValues = []
        listOfEnteredFieldsValues.clear()

        for fieldDescrAndFieldWidgets in self.listOfFieldDescrAndWidgets:
            fieldValue = self.getFieldValue(fieldDescrAndFieldWidgets)
            listOfEnteredFieldsValues.append(fieldValue)

        return listOfEnteredFieldsValues


    def getFieldValue(self, fieldDescrAndFieldWidgets: dict) -> str:
        fieldWidget = fieldDescrAndFieldWidgets["widgetForFieldValue"]
        fieldDescr = fieldDescrAndFieldWidgets["fieldDescr"]
        anyValueCheckBox = fieldDescrAndFieldWidgets["anyValueCheckBox"]

        if anyValueCheckBox.isChecked():
            if fieldDescr["fieldLength"] == 'undef.':
                fieldValue = "([0-1]{8})*"
            else:
                fieldValue = "x"
        elif isinstance(fieldWidget, QLineEdit):
            fieldValue = self.getFieldValueForLineEdit(fieldDescrAndFieldWidgets)
        elif isinstance(fieldWidget, QSpinBox):
            fieldValue = self.getFieldValurForSpinBox(fieldDescrAndFieldWidgets)
        elif isinstance(fieldWidget, QComboBox):
            fieldValue = fieldWidget.currentText().split(' - ')[0]
        else:
            fieldValue = ''

        return fieldValue


    def getFieldValurForSpinBox(self, fieldDescrAndFieldWidgets: dict) -> str:
        fieldWidget = fieldDescrAndFieldWidgets["widgetForFieldValue"]
        fieldValue = fieldWidget.value()
        fieldValueHex = hex(fieldValue)
        fieldValueHexStr = str(fieldValueHex)
        fieldValue = fieldValueHexStr.replace('0x', '')

        return fieldValue


    def getFieldValueForLineEdit(self, fieldDescrAndFieldWidgets: dict) -> str:
        fieldWidget = fieldDescrAndFieldWidgets["widgetForFieldValue"]
        fieldDescr = fieldDescrAndFieldWidgets["fieldDescr"]
        fieldValue = fieldWidget.text()

        if fieldValue != '' and fieldDescr["fieldLength"] == 'undef.' and len(fieldValue) % 2 == 1:
            fieldValue = "0" + fieldValue

        return fieldValue


    def setLengthValueForFieldWithRoleLength(self, listOfFieldValues: list) -> list:
        """

        :param listOfFieldValues:
        :return:
        """
        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        fieldWithLengthIndex = self.formatManager.getIndexOfFieldWithRoleLengthInMsgType(currentMsgType)

        if fieldWithLengthIndex is not None:
            fieldLengthFieldValue = self.getFieldValueForFieldLength()

            if fieldWithLengthIndex < len(listOfFieldValues):
                listOfFieldValues[fieldWithLengthIndex] = fieldLengthFieldValue
            else:
                listOfFieldValues.append(fieldLengthFieldValue)

        return listOfFieldValues


    def getFieldValueForFieldLength(self) -> str:
        anyValue = self.getIfFieldIsSetToAnyValue()

        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        intFieldLength = self.formatManager.getLengthOfFieldWithRoleLengthInMsgType(currentMsgType)

        if anyValue:
            fieldLengthInSymbols = intFieldLength // 4
            fieldValue = 'x' * fieldLengthInSymbols
        else:
            msgLength = self.getLenOfCurrentMsgInBytes()
            fieldValue = '{:0{}X}'.format(msgLength, intFieldLength // 4)

        return fieldValue


    def getIfFieldIsSetToAnyValue(self) -> bool:
        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        fieldWithLengthIndex = self.formatManager.getIndexOfFieldWithRoleLengthInMsgType(currentMsgType)

        if fieldWithLengthIndex < len(self.listOfFieldDescrAndWidgets):
            fieldDescrAndWidgetsForFieldWithLength = self.listOfFieldDescrAndWidgets[fieldWithLengthIndex]
            anyValue = fieldDescrAndWidgetsForFieldWithLength["anyValueCheckBox"].isChecked()
        else:
            anyValue = False

        return anyValue


    def getGroupedValuesList(self) -> list:
        groupedValuesList = []

        for widget in self.listWidgetTabs:
            widgetValue = self.getWidgetValue(widget)
            groupedValuesList.append(widgetValue)

        return groupedValuesList


    def getWidgetValue(self, widget):
        if isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QSpinBox):
            return widget.value()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        else:
            return ''


    def someUndefFieldContainsOddNumOfHexSymbols(self) -> bool:
        """
        :return:
        """
        listOfUndefFieldsStr = self.getListOfStrForUndefLenFields()

        fieldContainsOddNumOfHexSymbols = False

        for undefFieldStr in listOfUndefFieldsStr:
            if not self.undefFieldMarkedAsAnyValue(undefFieldStr) and \
                   self.undefFieldContainsOddNumOfHexSymbols(undefFieldStr):
                fieldContainsOddNumOfHexSymbols = True

        if fieldContainsOddNumOfHexSymbols:
            self.showErrorMessageBox(_('Length of field with undefined length does note fit in whole byte'),
                                     _('Amount of entered hex symbols must be even'))

        return fieldContainsOddNumOfHexSymbols


    def undefFieldContainsOddNumOfHexSymbols(self, undefFieldStr) -> bool:
        """
        :param undefFieldStr:
        :return:
        """
        if len(undefFieldStr) % 2 == 1:
            return True
        else:
            return False


    def undefFieldMarkedAsAnyValue(self, undefFieldStr) -> bool:
        """
        :param undefFieldStr:
        :return:
        """
        if undefFieldStr[0] == '(':
            return True
        else:
            return False


    def getListOfStrForUndefLenFields(self) -> list:
        """
        :return:
        """
        listOfUndefStr = []

        listOfHexFields = self.getListOfHexFields()

        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        msgInfoDict = self.formatManager.getInfoForMsgType(currentMsgType)
        self.msgCreator.setMsgType(currentMsgType)

        for index, hexField in enumerate(listOfHexFields):
            adjIndex = self.msgCreator.adjustIndexForMsgWithGroupedFieldsInMsgType(index)

            fieldDescrsList = msgInfoDict["fieldDescrsList"]
            fieldDescr = fieldDescrsList[adjIndex]

            if fieldDescr["fieldLength"] == 'undef.':
                listOfUndefStr.append(hexField)

        return listOfUndefStr


    def getListOfHexFields(self) -> list:
        msgHexStr = self.labelResultMsg.text()
        msgHexStr = msgHexStr.replace(_('MSG:'), '')
        msgHexStr = msgHexStr.replace(_('MSG (bin):'), '')
        msgHexStr = msgHexStr.replace('  ', ' ')
        msgHexStr = msgHexStr.strip()

        listOfHexFields = msgHexStr.split(' ')

        return listOfHexFields


    @pyqtSlot()
    def saveNamedRegexp(self) -> None:
        """
        :return:
        """
        regexpTitle = self.lineEditRegexpName.text()

        if self.someUndefFieldContainsOddNumOfHexSymbols() or \
           self.regexpTitleIsEmpty() or \
           self.regexpTitleIsNotUnique(regexpTitle):
            return

        regexpBinStr = self.getRegexpBinStr()

        managerRegexpList = managerNamedRegexp.ManagerNamedRegexp(self.profileTitle)
        newRegexpDict = {"regexpTitle": regexpTitle, "regexpBinStr": regexpBinStr}
        managerRegexpList.addNewNamedRegexp(newRegexpDict)

        self.showSuccessMessageBox(_("Regexp ") + regexpTitle + _(" added!"))

        self.signalNamedRegexpAdded.emit(regexpTitle, regexpBinStr)


    def regexpTitleIsNotUnique(self, regexpTitle: str) -> bool:
        regexpManager = managerNamedRegexp.ManagerNamedRegexp(self.profileTitle)
        allRegexpTitlesList = regexpManager.getAllNamedRegexpTitlesList()

        if regexpTitle in allRegexpTitlesList:
            strRegexpTitlesList = self.getStrRegexpTitlesList(allRegexpTitlesList)

            self.showErrorMessageBox(_('Msg regexp title is already in use!'),
                                     _('Enter unique msg regexp title. Regexp titles that are already in use:\n') +
                                     strRegexpTitlesList)
            return True
        else:
            return False


    def getStrRegexpTitlesList(self, allRegexpTitlesList: list) -> list:
        stringHandler = handlerString.HandlerString()
        strRegexpTitlesList = stringHandler.getStrOrderedListFromList(allRegexpTitlesList)

        return strRegexpTitlesList


    def getRegexpBinStr(self) -> str:
        textInResultMsg = self.labelResultMsg.text()
        msgInResultMsg = textInResultMsg.split(':')[1]
        msgInResultMsg = msgInResultMsg.strip()

        stringHandler = handlerString.HandlerString()
        msgBinStr = stringHandler.getWholeMsgBinStrFromHexStr(msgInResultMsg)

        regexpBinStr = msgBinStr.replace('x', '[0-1]')
        regexpBinStr = regexpBinStr.replace(' ', '')

        if regexpBinStr[0] != '^':
            regexpBinStr = '^' + regexpBinStr

        return regexpBinStr


    def regexpTitleIsEmpty(self) -> bool:
        """
        :return:
        """
        if self.lineEditRegexpName.text() == '':
            self.showErrorMessageBox(_('No regexp title entered!'))
            return True
        else:
            return False


    @pyqtSlot()
    def addNewTab(self):
        """
        Don't mind that monstrosity for now please
        :return:
        """
        nextTabIndex = self.tabs.currentIndex() + 1
        currentTabIsTubWithPlusForAddingNewTabs = (self.tabs.currentIndex() > 0 and nextTabIndex == self.tabs.count())

        if currentTabIsTubWithPlusForAddingNewTabs:
            groupedFieldsLine = 0

            gridLayForGroupedFields = self.getGridLayForGroupedFields()

            self.prepareTabs()

            self.fieldDescrAndWidgetsDict = {"fieldDescr": dict(), "widgetForFieldValue": QWidget(), "anyValueCheckBox": QCheckBox()}
            for widgetGrouped in self.listWidgetTabs:
                if isinstance(widgetGrouped, QGridLayout) or isinstance(widgetGrouped, QGroupBox):
                    continue
                widget = self.getWidgetForGroupedWidgets(groupedFieldsLine, widgetGrouped)

                widgetColumnOnGrid = self.getWidgetColumnForGroupedWidgets(widgetGrouped)
                gridLayForGroupedFields.addWidget(widget, groupedFieldsLine, widgetColumnOnGrid)

                if isinstance(widgetGrouped, QCheckBox):
                    # Every line ends on any value checkbox
                    groupedFieldsLine += 1
                    self.addFieldDescrAndWidgetsDict()

            self.updateCreatedMsgLabel()


    def addFieldDescrAndWidgetsDict(self):
        lastIndexBeforeTale = self.getLastIndexBeforeTale()
        self.listOfFieldDescrAndWidgets.insert(lastIndexBeforeTale, self.fieldDescrAndWidgetsDict)


    def getLastIndexBeforeTale(self):
        currentMsgType = self.comboBoxCurrentMsgType.currentText()
        countOfTaleFields = self.formatManager.getCountOfTaleFieldsInMsgType(currentMsgType)
        lenOfFieldWidgetsAndDescrsList = len(self.listOfFieldDescrAndWidgets)

        lastIndexBeforeTale = lenOfFieldWidgetsAndDescrsList - countOfTaleFields

        return lastIndexBeforeTale


    def getWidgetForGroupedWidgets(self, groupedFieldsLine, widgetGrouped):
        if isinstance(widgetGrouped, QLabel):
            widget = QLabel(widgetGrouped.text())
        elif isinstance(widgetGrouped, QCheckBox):
            widget = QCheckBox()
            widget.setText(_('Any value'))

            widget.clicked.connect(self.updateCreatedMsgLabel)

            self.fieldDescrAndWidgetsDict["anyValueCheckBox"] = widget
        else:
            currentMsgType = self.comboBoxCurrentMsgType.currentText()
            indexOfStartGroupedField = self.formatManager.getIndexOfFirstFieldInGroupInMsgType(currentMsgType)

            widget = self.getWidgetForEnteringValue(self.currentMsgDescrList[indexOfStartGroupedField + groupedFieldsLine])
            self.fieldDescrAndWidgetsDict["widgetForFieldValue"] = widget

        self.listWidgetTabs.append(widget)

        return widget


    def getWidgetColumnForGroupedWidgets(self, widgetGrouped) -> int:
        if isinstance(widgetGrouped, QLabel):
            widgetPosition = 0
        elif isinstance(widgetGrouped, QCheckBox):
            widgetPosition = 2
        else:
            widgetPosition = 1

        return widgetPosition


    def getGridLayForGroupedFields(self):
        gridLayGroupedFields = QGridLayout(self)

        groupBoxGroupedFields = QGroupBox(self)
        groupBoxGroupedFields.setLayout(gridLayGroupedFields)
        self.listWidgetTabs.append(groupBoxGroupedFields)
        self.tabs.addTab(groupBoxGroupedFields, _('Group'))

        return gridLayGroupedFields


    def prepareTabs(self):
        self.tabs.addTab(QWidget(), '+')

        indexBefore = self.tabs.currentIndex()
        self.tabs.removeTab(indexBefore)

        tabBar = self.tabs.findChild(QTabBar)
        tabBar.setTabButton(self.tabs.count() - 1, QTabBar.RightSide, None)
        tabBar.setTabButton(self.tabs.count() - 1, QTabBar.LeftSide, None)
