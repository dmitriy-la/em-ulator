import gettext

from PyQt5.Qt import Qt
from PyQt5.QtCore import QSize, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAbstractItemView, QButtonGroup, QCheckBox, QFrame
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QHeaderView, QLabel
from PyQt5.QtWidgets import QLineEdit, QPushButton, QRadioButton
from PyQt5.QtWidgets import QSpinBox, QTableView, QVBoxLayout

import src.datamodels.dataModelValues as dataModelValues
import src.ui.widgets.bigIntSpinBox as bigIntSpinBox
import src.ui.windows.windowProfiledWindow as windowProfiledWindow

_ = gettext.gettext


class WindowFieldEditor(windowProfiledWindow.WindowProfiledWindow):
    signalFieldAddedFromFieldEditor = pyqtSignal(dict)

    def __init__(self, profileTitle: str, parent=None):
        super().__init__(profileTitle, parent)
        self.valueModel = dataModelValues.DataModelValues()

        self.lengthModeBytes = False

        self.initUI()


    def initUI(self):
        self.setWindowProperties()

        principalGroupBoxLayout = self.getPrincipalGroupBoxLayout()

        self.addSectionForEditingFieldTitle(principalGroupBoxLayout)
        self.addSectionForEditingFieldLength(principalGroupBoxLayout)
        self.addSectionForEditingFieldValues(principalGroupBoxLayout)
        self.addSectionForEditingFieldRole(principalGroupBoxLayout)

        self.addCheckBoxMarkFieldToBeCopiedInAutoresponse(principalGroupBoxLayout)

        self.addButtonsAddAndCloseLayout(principalGroupBoxLayout)

        self.show()


    def setWindowProperties(self):
        self.setWindowTitle(_('Field Editor'))

        self.setFocusPolicy(Qt.ClickFocus)
        self.setModal(True)

        xCoord = 10
        yCoord = 10
        windowHeight = 200
        windowWidth = 320

        flags = self.windowFlags()
        self.setWindowFlags(int(flags) | Qt.Tool)

        self.setGeometry(xCoord, yCoord, windowWidth, windowHeight)


    def getPrincipalGroupBoxLayout(self):
        principalLayout = QHBoxLayout(self)
        self.principalGroupBox = self.addPrincipalGroupBox(principalLayout)

        vLayoutPrincipalGroupBox = QVBoxLayout(self.principalGroupBox)
        self.principalGroupBox.setLayout(vLayoutPrincipalGroupBox)

        return vLayoutPrincipalGroupBox


    def addPrincipalGroupBox(self, principalLayout):
        principalGroupBox = QGroupBox(self)
        principalGroupBox.setTitle(_('Field Editor'))
        principalLayout.addWidget(principalGroupBox)

        return principalGroupBox


    def addSectionForEditingFieldTitle(self, vLayout):
        self.addLabelFieldTitle(vLayout)
        self.lineEditFieldTitle = self.addLineEditFieldTitle(vLayout)
        self.addLine(vLayout)
        vLayout.addSpacing(8)


    def addLabelFieldTitle(self, vLayout):
        labelFieldTitle = QLabel(self.principalGroupBox)
        labelFieldTitle.setText(_('Field title:'))

        vLayout.addWidget(labelFieldTitle)


    def addLineEditFieldTitle(self, vLayout):
        lineEditFieldTitle = QLineEdit(self.principalGroupBox)
        lineEditFieldTitle.setText(_('Field'))

        vLayout.addWidget(lineEditFieldTitle)

        return lineEditFieldTitle


    def addSectionForEditingFieldLength(self, vLayout):
        self.addLengthTypeHLay(vLayout)
        self.addLengthValueHLay(vLayout)
        self.addLine(vLayout)
        vLayout.addSpacing(8)


    def addLengthTypeHLay(self, vLayout):
        hLayoutLengthType = QHBoxLayout(self.principalGroupBox)

        self.addLabelFieldLength(hLayoutLengthType)
        self.addRadioButtonBytes(hLayoutLengthType)
        self.addRadioButtonBites(hLayoutLengthType)

        hLayoutLengthType.addStretch(1)

        vLayout.addLayout(hLayoutLengthType)


    def addLengthValueHLay(self, vLayout):
        hLayoutLengthValue = QHBoxLayout(self.principalGroupBox)

        self.spinBoxLength = self.addSpinBoxLength(hLayoutLengthValue)
        self.checkBoxMarkFieldLengthAsUndefined = self.addCheckBoxMarkFieldLengthAsUndefined(hLayoutLengthValue)

        vLayout.addLayout(hLayoutLengthValue)


    def addSectionForEditingFieldValues(self, vLayout):
        self.addLabelValues(vLayout)
        self.addValuesEditHLay(vLayout)
        self.addTableAndButtonsHLay(vLayout)
        self.addLine(vLayout)
        vLayout.addSpacing(8)


    def addLabelValues(self, vLayout):
        labelValues = QLabel(self.principalGroupBox)
        labelValues.setText(_('Set up values allowed for this field (any value is allowed by default):'))

        vLayout.addWidget(labelValues)


    def addValuesEditHLay(self, vLayout):
        hLayoutValuesEdit = QHBoxLayout(self.principalGroupBox)

        self.addLabelValue(hLayoutValuesEdit)
        self.spinBoxValueHex = self.addSpinBoxWithOneHexValue(hLayoutValuesEdit)
        self.addLabelValueMeaning(hLayoutValuesEdit)

        self.textEditValueMeaning = self.addTextEditValueMeaning(hLayoutValuesEdit)

        vLayout.addLayout(hLayoutValuesEdit)


    def addLabelValue(self, hLayoutValuesEdit):
        labelValue = QLabel(self.principalGroupBox)
        labelValue.setText(_('Value (Hex)'))

        hLayoutValuesEdit.addWidget(labelValue)


    def addSpinBoxWithOneHexValue(self, hLayoutValuesEdit):
        spinBoxValueHex = bigIntSpinBox.BigIntSpinBox(self.principalGroupBox)
        # spinBoxValueHex.setDisplayIntegerBase(16)
        spinBoxValueHex.setValue(0)
        spinBoxValueHex.setMinimumWidth(90)
        spinBoxValueHex.setMaximumWidth(200)
        spinBoxValueHex.setBitLengthToDisplay(self.spinBoxLength.value())

        hLayoutValuesEdit.addWidget(spinBoxValueHex)

        return spinBoxValueHex


    def addLabelValueMeaning(self, hLayoutValuesEdit):
        labelValueMeaning = QLabel(self.principalGroupBox)
        labelValueMeaning.setText(_('Meaning'))

        hLayoutValuesEdit.addWidget(labelValueMeaning)


    def addTextEditValueMeaning(self, hLayoutValuesEdit):
        textEditValueMeaning = QLineEdit(self.principalGroupBox)
        textEditValueMeaning.setText(_('Meaning'))

        hLayoutValuesEdit.addWidget(textEditValueMeaning)

        return textEditValueMeaning


    def addTableAndButtonsHLay(self, vLayout):
        hLayoutTableAndButtons = QHBoxLayout(self.principalGroupBox)
        self.tableView = self.addTableViewForValues(hLayoutTableAndButtons)

        vLayoutButtons = QVBoxLayout(self.principalGroupBox)

        self.buttonAddValue = self.addButtonAddValue(vLayoutButtons)
        self.buttonRemoveValue = self.addButtonRemoveValue(vLayoutButtons)
        self.buttonClearAll = self.addButtonClearAll(vLayoutButtons)

        vLayoutButtons.addStretch(1)

        hLayoutTableAndButtons.addLayout(vLayoutButtons)

        vLayout.addLayout(hLayoutTableAndButtons)


    def addButtonAddValue(self, vLayoutButtons) -> QPushButton:
        buttonAddValue = QPushButton(self.principalGroupBox)
        buttonAddValue.clicked.connect(self.onClickAddValueAndMeaning)

        pixmap = QPixmap('../icons/add-document.png')
        saveIcon = QIcon(pixmap)
        buttonAddValue.setIcon(saveIcon)
        buttonAddValue.setIconSize(QSize(15, 15))

        vLayoutButtons.addWidget(buttonAddValue)

        return buttonAddValue


    def addButtonRemoveValue(self, vLayoutButtons) -> QPushButton:
        buttonRemoveValue = QPushButton(self.principalGroupBox)
        buttonRemoveValue.clicked.connect(self.onClickDelValueRow)

        pixmap = QPixmap('../icons/trash.png')
        saveIcon = QIcon(pixmap)
        buttonRemoveValue.setIcon(saveIcon)
        buttonRemoveValue.setIconSize(QSize(15, 15))

        vLayoutButtons.addWidget(buttonRemoveValue)

        return buttonRemoveValue


    def addButtonClearAll(self, vLayoutButtons) -> QPushButton:
        buttonClearAll = QPushButton(self.principalGroupBox)
        buttonClearAll.clicked.connect(self.onClickClearAllRows)

        pixmap = QPixmap('../icons/broom.png')
        saveIcon = QIcon(pixmap)
        buttonClearAll.setIcon(saveIcon)
        buttonClearAll.setIconSize(QSize(15, 15))

        vLayoutButtons.addWidget(buttonClearAll)

        return buttonClearAll


    def addTableViewForValues(self, hLayoutTableAndButtons):
        tableView = QTableView(self.principalGroupBox)
        tableView.setModel(self.valueModel)
        tableView.setToolTip(_('Edit table by adding values'))
        tableView.horizontalHeader().setStretchLastSection(True)

        tableView.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        tableView.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        tableView.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        hLayoutTableAndButtons.addWidget(tableView)

        return tableView


    def addRadioButtonBites(self, hLayoutLengthType):
        radioButtonBites = QRadioButton(self.principalGroupBox)

        radioButtonBites.setText(_('bits'))
        radioButtonBites.setChecked(True)
        radioButtonBites.clicked.connect(self.switchLengthToBits)

        hLayoutLengthType.addWidget(radioButtonBites)


    def addRadioButtonBytes(self, hLayoutLengthType):
        radioButtonBytes = QRadioButton(self.principalGroupBox)

        radioButtonBytes.setText(_('bytes'))
        radioButtonBytes.clicked.connect(self.switchLengthToBytes)

        hLayoutLengthType.addWidget(radioButtonBytes)


    def addLabelFieldLength(self, hLayoutLengthType):
        labelFieldLength = QLabel(self.principalGroupBox)
        labelFieldLength.setText(_('Field\'s length in'))

        hLayoutLengthType.addWidget(labelFieldLength)


    def addCheckBoxMarkFieldLengthAsUndefined(self, hLayoutLengthValue):
        checkBoxMarkFieldLengthAsUndefined = QCheckBox(self.principalGroupBox)

        checkBoxMarkFieldLengthAsUndefined.setText(_('Undefined field length'))
        checkBoxMarkFieldLengthAsUndefined.clicked.connect(self.onClickCheckboxLenUndef)

        hLayoutLengthValue.addWidget(checkBoxMarkFieldLengthAsUndefined)

        return checkBoxMarkFieldLengthAsUndefined


    def addSpinBoxLength(self, hLayoutLengthValue):
        spinBoxLength = QSpinBox(self.principalGroupBox)
        spinBoxLength.setValue(8)
        spinBoxLength.setMinimum(1)
        spinBoxLength.setMaximum(999)
        spinBoxLength.valueChanged.connect(self.onLengthChanged)

        hLayoutLengthValue.addWidget(spinBoxLength)

        return spinBoxLength


    def addLine(self, vLayout):
        lineBeforeLength = QFrame(self.principalGroupBox)

        lineBeforeLength.setFrameShape(QFrame.HLine)
        lineBeforeLength.setFrameShadow(QFrame.Raised)

        vLayout.addWidget(lineBeforeLength)


    def addSectionForEditingFieldRole(self, vLayout):
        vLayoutFieldRole = QVBoxLayout(self.principalGroupBox)

        self.buttonRolesGroup = QButtonGroup(self.principalGroupBox)

        labelFieldRole = QLabel(self.principalGroupBox)
        labelFieldRole.setText(_('Field content\'s type:'))
        vLayoutFieldRole.addWidget(labelFieldRole)

        self.addRadioButtonRoleLength(vLayoutFieldRole)
        self.addRadioButtonRoleType(vLayoutFieldRole)
        self.addRadioButtonRoleId(vLayoutFieldRole)
        self.addRadioButtonRoleCrc(vLayoutFieldRole)
        self.addRadioButtonRoleOther(vLayoutFieldRole)

        vLayoutFieldRole.addStretch(1)

        vLayout.addLayout(vLayoutFieldRole)


    def addRadioButtonRoleLength(self, vLayoutFieldRole):
        self.radioButtonRoleLength = QRadioButton()
        self.radioButtonRoleLength.setText(_('message length'))
        self.radioButtonRoleLength.setChecked(False)

        self.buttonRolesGroup.addButton(self.radioButtonRoleLength)

        vLayoutFieldRole.addWidget(self.radioButtonRoleLength)


    def addRadioButtonRoleType(self, vLayoutFieldRole):
        self.radioButtonRoleType = QRadioButton()
        self.radioButtonRoleType.setText(_('message type'))
        self.radioButtonRoleType.setChecked(False)

        self.buttonRolesGroup.addButton(self.radioButtonRoleType)

        vLayoutFieldRole.addWidget(self.radioButtonRoleType)


    def addRadioButtonRoleId(self, vLayoutFieldRole):
        self.radioButtonRoleId = QRadioButton()
        self.radioButtonRoleId.setText(_('message identification number'))
        self.radioButtonRoleId.setChecked(False)

        self.buttonRolesGroup.addButton(self.radioButtonRoleId)

        vLayoutFieldRole.addWidget(self.radioButtonRoleId)


    def addRadioButtonRoleCrc(self, vLayoutFieldRole):
        self.radioButtonRoleCrc = QRadioButton()
        self.radioButtonRoleCrc.setText(_('control sum'))
        self.radioButtonRoleCrc.setChecked(False)

        self.buttonRolesGroup.addButton(self.radioButtonRoleCrc)

        vLayoutFieldRole.addWidget(self.radioButtonRoleCrc)


    def addRadioButtonRoleOther(self, vLayoutFieldRole):
        self.radioButtonRoleOther = QRadioButton()
        self.radioButtonRoleOther.setText(_('other'))
        self.radioButtonRoleOther.setChecked(True)

        self.buttonRolesGroup.addButton(self.radioButtonRoleOther)

        vLayoutFieldRole.addWidget(self.radioButtonRoleOther)


    def addCheckBoxMarkFieldToBeCopiedInAutoresponse(self, vLayout):
        self.checkBoxMarkFieldToBeCopiedInAutoresponse = QCheckBox(self.principalGroupBox)
        self.checkBoxMarkFieldToBeCopiedInAutoresponse.setText(_('Copy field from received msg in autoresponse'))

        vLayout.addWidget(self.checkBoxMarkFieldToBeCopiedInAutoresponse)


    def addButtonsAddAndCloseLayout(self, vLayout):
        hLayoutAddAndClose = QHBoxLayout(self.principalGroupBox)
        hLayoutAddAndClose.addStretch(1)

        self.addButtonAddField(hLayoutAddAndClose)
        self.addButtonClose(hLayoutAddAndClose)

        vLayout.addLayout(hLayoutAddAndClose)


    def addButtonClose(self, hLayoutAddOrStop):
        hLayoutAddOrStop.addWidget(self.buttonClose)


    def addButtonAddField(self, hLayoutAddOrStop):
        self.buttonSave.setText(_('Add field'))

        self.buttonSave.clicked.connect(self.addNewField)

        hLayoutAddOrStop.addWidget(self.buttonSave)


    @pyqtSlot()
    def switchLengthToBytes(self):
        self.lengthModeBytes = True
        self.onLengthChanged()


    @pyqtSlot()
    def switchLengthToBits(self):
        self.lengthModeBytes = False
        self.onLengthChanged()


    @pyqtSlot()
    def onClickCheckboxLenUndef(self):
        if self.checkBoxMarkFieldLengthAsUndefined.isChecked():
            self.disableWidgets()
        else:
            self.enableWidgets()


    def disableWidgets(self):
        self.spinBoxLength.setDisabled(True)
        self.buttonAddValue.setDisabled(True)
        self.buttonClearAll.setDisabled(True)
        self.buttonRemoveValue.setDisabled(True)
        self.spinBoxValueHex.setDisabled(True)
        self.tableView.setDisabled(True)
        self.textEditValueMeaning.setDisabled(True)


    def enableWidgets(self):
        self.spinBoxLength.setEnabled(True)
        self.buttonAddValue.setEnabled(True)
        self.buttonClearAll.setEnabled(True)
        self.buttonRemoveValue.setEnabled(True)
        self.spinBoxValueHex.setEnabled(True)
        self.tableView.setEnabled(True)
        self.textEditValueMeaning.setEnabled(True)


    @pyqtSlot()
    def onLengthChanged(self):
        if self.lengthModeBytes:
            bitLength = self.spinBoxLength.value() * 8
        else:
            bitLength = self.spinBoxLength.value()

        self.spinBoxValueHex.setBitLengthToDisplay(bitLength)


    @pyqtSlot()
    def onClickDelValueRow(self):
        selectionModel = self.tableView.selectionModel()
        indexes = selectionModel.selectedIndexes()

        if indexes:
            rowToDel = indexes[0].row()
            self.valueModel.removeRows(rowToDel, 1)


    @pyqtSlot()
    def onClickClearAllRows(self):
        rowCount = self.valueModel.rows
        self.valueModel.removeRows(0, rowCount)
        self.spinBoxValueHex.setValue(0)


    @pyqtSlot()
    def onClickAddValueAndMeaning(self):
        if self.userEnteredValueIsUnique():
            self.valueModel.appendValueRow(self.spinBoxValueHex.text(), self.textEditValueMeaning.text())
            self.incrementValueHex()


    def incrementValueHex(self):
        newLengthValue = self.spinBoxValueHex.value()
        newLengthValue += 1
        self.spinBoxValueHex.setValue(newLengthValue)


    def userEnteredValueIsUnique(self) -> bool:
        newValue = self.spinBoxValueHex.text()

        for row in self.valueModel.valuesList:
            if newValue in row.values():
                return False

        return True


    @pyqtSlot()
    def addNewField(self):
        fieldDict = {"fieldTitle": self.lineEditFieldTitle.text(),
                     "fieldLength": self.formFieldLengthString(),
                     "fieldRole": self.getFieldRole(),
                     "fieldToBeCopiedInAutoResp": self.checkBoxMarkFieldToBeCopiedInAutoresponse.isChecked(),
                     "fieldToSwapWithInAutoresp": '',
                     "fieldValuesList": self.valueModel.valuesList[:]}

        self.signalFieldAddedFromFieldEditor.emit(fieldDict)

        self.showSuccessMessageBox(_('Field \"') + self.lineEditFieldTitle.text() + _('\" appended!'))

        self.resetAllEnteredData()


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


    def formFieldLengthString(self) -> str:
        length = ''
        if self.checkBoxMarkFieldLengthAsUndefined.isChecked():
            length += 'undef.'
        elif self.lengthModeBytes:
            length += str(8 * self.spinBoxLength.value())
        else:
            length += str(self.spinBoxLength.value())
        return length


    def resetAllEnteredData(self):
        self.checkBoxMarkFieldToBeCopiedInAutoresponse.setChecked(False)
        self.checkBoxMarkFieldLengthAsUndefined.setChecked(False)

        self.spinBoxLength.setEnabled(True)
        self.spinBoxValueHex.setValue(0)

        rowCount = self.valueModel.rows
        self.valueModel.removeRows(0, rowCount)
