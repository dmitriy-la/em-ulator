import gettext

from PyQt5.Qt import Qt
from PyQt5.QtCore import QRegExp, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QComboBox, QGridLayout, QGroupBox, QLabel
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QListWidget
from PyQt5.QtWidgets import QPushButton, QStackedWidget, QVBoxLayout

import src.handlers.handlerString as handlerString
import src.managers.managerAutoresponseSettings as managerAutoresponseSettings
import src.managers.managerNamedMsg as managerNamedMsg
import src.ui.windows.windowNamedMsgEditor as windowNamedMsgEditor
import src.ui.windows.windowProfiledWindow as windowProfiledWindow


_ = gettext.gettext

ROW_INDEX_OF_ACTION_TYPE_CHANGE_MODE = 0
ROW_INDEX_OF_ACTION_TYPE_RESPOND_WITH_RECEIVED_MSG_WITH_ASSIGNING_FIELDS = 1
ROW_INDEX_OF_ACTION_TYPE_RESPOND_WITH_NAMED_MSG = 2
ROW_INDEX_OF_ACTION_TYPE_RESPOND_WITH_FEW_NAMED_MSG = 3


class WindowAutorespActionEditor(windowProfiledWindow.WindowProfiledWindow):
    signalNewActionCreated = pyqtSignal(dict)

    def __init__(self, profileTitle: str, parent=None):
        super().__init__(profileTitle, parent)
        self.comboBoxList = []
        self.comboBoxLineCounter = 0

        self.listOfWidgetsWithFieldTitlesAndValues = []
        self.fieldTitlesLineCounter = 0

        self.managerNamedMsg = managerNamedMsg.ManagerNamedMsg(self.profileTitle)
        self.managerAutoresp = managerAutoresponseSettings.ManagerAutoresponseSettings(self.profileTitle)

        self.initUI()


    def initUI(self) -> None:
        self.setWindowProperties()

        principalLayout = QVBoxLayout(self)

        self.addLabelActionTitle(principalLayout)
        self.lineEditActionTitle = self.addLineEditActionTitle(principalLayout)

        self.addLabelActionType(principalLayout)

        self.addLayoutWithListOfActionTypesAndCorrespondingWidgetsForEdit(principalLayout)

        self.addLayoutForSaveAndCloseButtons(principalLayout)

        self.show()


    def setWindowProperties(self) -> None:
        title = _("Actions Editor")
        self.setWindowTitle(title)

        xCoord = 330
        yCoord = 200
        height = 400
        width = 600
        self.setGeometry(xCoord, yCoord, width, height)

        self.setFocusPolicy(Qt.ClickFocus)
        self.setModal(True)


    def addLabelActionTitle(self, principalLayout: QVBoxLayout) -> None:
        labelActionTitle = QLabel(_('Action title:'))
        principalLayout.addWidget(labelActionTitle)


    def addLineEditActionTitle(self, principalLayout: QVBoxLayout) -> QLineEdit:
        lineEditActionTitle = QLineEdit(self)
        principalLayout.addWidget(lineEditActionTitle)

        return lineEditActionTitle


    def addLabelActionType(self, principalLayout: QVBoxLayout) -> None:
        labelActionType = QLabel(_('Action type:'))
        principalLayout.addWidget(labelActionType)


    def addLayoutWithListOfActionTypesAndCorrespondingWidgetsForEdit(self, principalLayout: QVBoxLayout) -> None:
        hLay = QHBoxLayout(self)

        self.actionTypesList = self.addListWithActionTypes(hLay)

        self.stackedWidgetsForDifferentActionTypes = self.addStackedWidgetsSectionForDifferentActionTypes(hLay)

        principalLayout.addLayout(hLay)


    def addListWithActionTypes(self, hLay: QHBoxLayout) -> QListWidget:
        actionTypesListWidget = QListWidget(self)

        actionTypes = [  # _('Save in separate log'),
            _('Change mode'),
            _('Change some fields values and respond with the same MSG'),
            _('Send named MSG'),
            _('Send few named MSG')]
        actionTypesListWidget.addItems(actionTypes)

        actionTypesListWidget.setCurrentRow(0)

        actionTypesListWidget.setMinimumWidth(380)

        actionTypesListWidget.currentItemChanged.connect(self.switchActionEditors)

        hLay.addWidget(actionTypesListWidget)

        return actionTypesListWidget


    def addStackedWidgetsSectionForDifferentActionTypes(self, hLay: QHBoxLayout) -> QStackedWidget:
        stackedWidgetsForDifferentActionTypes = QStackedWidget(self)

        # groupBoxWithLabelRemember = self.getGroupBoxWithLabel(_('Keep track of receiving of this msg'))
        # self.stackedWidgetsForDifferentActionTypes.insertWidget(0, groupBoxWithLabelRemember)

        groupBoxForChoosingAutorespModes = self.getGroupBoxWithAutorespModes()
        stackedWidgetsForDifferentActionTypes.insertWidget(ROW_INDEX_OF_ACTION_TYPE_CHANGE_MODE,
                                                           groupBoxForChoosingAutorespModes)

        groupBoxRespondWithReceivedMsgWithAssigningValueToFields = self.getGroupBoxReceivedMsgWithAssigningValueToFields()
        stackedWidgetsForDifferentActionTypes.insertWidget(ROW_INDEX_OF_ACTION_TYPE_RESPOND_WITH_RECEIVED_MSG_WITH_ASSIGNING_FIELDS,
                                                           groupBoxRespondWithReceivedMsgWithAssigningValueToFields)

        groupBoxOneNamedMsg = self.getGroupBoxWithNamedMsgList()
        stackedWidgetsForDifferentActionTypes.insertWidget(ROW_INDEX_OF_ACTION_TYPE_RESPOND_WITH_NAMED_MSG,
                                                           groupBoxOneNamedMsg)

        groupBoxFewNamedMsg = self.getGroupBoxWithNamedMsgListForFewMsg()
        stackedWidgetsForDifferentActionTypes.insertWidget(ROW_INDEX_OF_ACTION_TYPE_RESPOND_WITH_FEW_NAMED_MSG,
                                                           groupBoxFewNamedMsg)

        hLay.addWidget(stackedWidgetsForDifferentActionTypes)

        return stackedWidgetsForDifferentActionTypes


    def getGroupBoxWithAutorespModes(self) -> QGroupBox:
        """
        :return:
        """
        comboGroup = QGroupBox()

        vLayChangeModes = self.getVLayForChangingModes()

        comboGroup.setLayout(vLayChangeModes)

        return comboGroup


    def getVLayForChangingModes(self) -> QVBoxLayout:
        vLayChangeModes = QVBoxLayout(self)

        labelNewMode = QLabel(_('New mode:'))
        vLayChangeModes.addWidget(labelNewMode)

        self.comboBoxForChoosingModes = self.getComboBoxWithAutorespModes()
        vLayChangeModes.addWidget(self.comboBoxForChoosingModes)

        vLayChangeModes.addStretch()

        return vLayChangeModes


    def getComboBoxWithAutorespModes(self) -> QComboBox:
        """
        :return:
        """
        autorespModesList = self.managerAutoresp.getListOfAutorespModesTitles()
        comboBoxWithAutorespModes = QComboBox()

        comboBoxWithAutorespModes.addItem('')
        comboBoxWithAutorespModes.addItems(autorespModesList)

        return comboBoxWithAutorespModes


    def getGroupBoxWithLabel(self, labelText: str) -> QGroupBox:
        """
        :param labelText:
        :return:
        """
        comboGroup = QGroupBox()

        vLayLabel = QVBoxLayout()
        labelRemember = QLabel(labelText)

        vLayLabel.addWidget(labelRemember)

        vLayLabel.addStretch()

        comboGroup.setLayout(vLayLabel)

        return comboGroup


    def getGroupBoxReceivedMsgWithAssigningValueToFields(self) -> QGroupBox:
        """
        :return:
        """
        groupBox = QGroupBox()

        self.gridLayFieldTitlesAndValuesStack = self.getGridLayFieldTitlesAndValuesStack()

        vLayForGrid = self.getVLayFromGridLay(self.gridLayFieldTitlesAndValuesStack)
        groupBox.setLayout(vLayForGrid)

        self.fieldTitlesLineCounter += 2

        return groupBox


    def getGridLayFieldTitlesAndValuesStack(self) -> QGridLayout:
        gridLayFieldTitlesAndValuesStack = QGridLayout(self)

        self.addHeaderLabels(gridLayFieldTitlesAndValuesStack)
        self.addFirstLineEditsForEnteringFieldTitleAndFieldValue(gridLayFieldTitlesAndValuesStack)
        self.addButtonForAddingFieldTitleAndValueLine(gridLayFieldTitlesAndValuesStack)

        return gridLayFieldTitlesAndValuesStack


    def addHeaderLabels(self, gridLayFieldTitlesAndValuesStack: QGridLayout) -> None:
        labelEnterFieldTitle = QLabel(_('Field title:'))
        gridLayFieldTitlesAndValuesStack.addWidget(labelEnterFieldTitle, 0, 0)

        labelEnterNewFieldValue = QLabel(_('Field value (HEX):'))
        gridLayFieldTitlesAndValuesStack.addWidget(labelEnterNewFieldValue, 0, 1)


    def addFirstLineEditsForEnteringFieldTitleAndFieldValue(self, gridLayFieldTitlesAndValuesStack: QGridLayout) -> None:
        lineEditWithFieldTitle = QLineEdit()
        gridLayFieldTitlesAndValuesStack.addWidget(lineEditWithFieldTitle, 1, 0)

        lineEditWithFieldValue = self.getLineEditWithFieldValue()
        gridLayFieldTitlesAndValuesStack.addWidget(lineEditWithFieldValue, 1, 1)

        dictWithFieldTitleAndValue = {"lineEditWithFieldTitle": lineEditWithFieldTitle,
                                      "lineEditWithFieldValue": lineEditWithFieldValue}

        self.listOfWidgetsWithFieldTitlesAndValues.append(dictWithFieldTitleAndValue)


    def getLineEditWithFieldValue(self) -> QLineEdit:
        lineEditWithFieldValue = QLineEdit()

        hexRegexp = QRegExp("[0-9A-Fa-f]*")
        hexValidator = QRegExpValidator(hexRegexp)
        lineEditWithFieldValue.setValidator(hexValidator)

        return lineEditWithFieldValue


    def addButtonForAddingFieldTitleAndValueLine(self, gridLayFieldTitlesAndValuesStack: QGridLayout) -> None:
        """
        :return:
        """
        buttonAddFieldTitleAndValueLine = QPushButton('+')

        buttonAddFieldTitleAndValueLine.setMaximumWidth(25)
        buttonAddFieldTitleAndValueLine.clicked.connect(self.addFieldTitleAndValueLine)

        gridLayFieldTitlesAndValuesStack.addWidget(buttonAddFieldTitleAndValueLine, 0, 2)


    def getVLayFromGridLay(self, gridLayFieldTitlesAndValuesStack: QGridLayout) -> QVBoxLayout:
        vLayForGrid = QVBoxLayout(self)

        vLayForGrid.addLayout(gridLayFieldTitlesAndValuesStack)
        vLayForGrid.addStretch()

        return vLayForGrid


    def getGroupBoxWithNamedMsgList(self) -> QGroupBox:
        comboGroup = QGroupBox()

        self.comboBoxForChoosingSingleNamedMsg = self.getComboBoxWithNamedMsg()

        vLaySingleComboBox = QVBoxLayout(self)
        vLaySingleComboBox.addWidget(self.comboBoxForChoosingSingleNamedMsg)
        vLaySingleComboBox.addStretch()

        self.addButtonForCreatingNewNamedMsg(vLaySingleComboBox)

        comboGroup.setLayout(vLaySingleComboBox)

        return comboGroup


    def getComboBoxWithNamedMsg(self) -> QComboBox:
        """
        :return:
        """
        namedMsgsList = self.managerNamedMsg.getAllNamedMsgList()
        comboBoxForChoosingNamedMsg = QComboBox()

        comboBoxForChoosingNamedMsg.addItem('')
        for namedMsgDescr in namedMsgsList:
            comboBoxForChoosingNamedMsg.addItem(namedMsgDescr["msgTitle"])

        return comboBoxForChoosingNamedMsg


    def addButtonForCreatingNewNamedMsg(self, vLaySingleComboBox: QVBoxLayout) -> None:
        self.buttonForCreatingNewNamedMsg = QPushButton(_('+ Create named msg'))
        self.buttonForCreatingNewNamedMsg.clicked.connect(self.createNewNamedMsg)

        vLaySingleComboBox.addWidget(self.buttonForCreatingNewNamedMsg)


    def getGroupBoxWithNamedMsgListForFewMsg(self) -> QGroupBox:
        """
        :return:
        """
        comboGroup = QGroupBox()

        self.gridLayFewNamedMsgComboBoxStack = QGridLayout(self)

        comboBoxForChoosingNamedMsg = self.getComboBoxWithNamedMsg()
        self.gridLayFewNamedMsgComboBoxStack.addWidget(comboBoxForChoosingNamedMsg, 0, 0)

        buttonAddNamedMsg = self.getButtonAddComboBoxLine()
        self.gridLayFewNamedMsgComboBoxStack.addWidget(buttonAddNamedMsg, 0, 1)

        vLayForGrid = QVBoxLayout(self)
        vLayForGrid.addLayout(self.gridLayFewNamedMsgComboBoxStack)
        vLayForGrid.addStretch()

        self.addButtonForCreatingNewNamedMsg(vLayForGrid)

        comboGroup.setLayout(vLayForGrid)

        self.comboBoxList.append(comboBoxForChoosingNamedMsg)
        self.comboBoxLineCounter += 1

        return comboGroup


    def getButtonAddComboBoxLine(self) -> QPushButton:
        """
        :return:
        """
        buttonAddNamedMsg = QPushButton('+')
        buttonAddNamedMsg.setMaximumWidth(25)
        buttonAddNamedMsg.clicked.connect(self.addNamedComboBoxLine)

        return buttonAddNamedMsg


    def addLayoutForSaveAndCloseButtons(self, principalLayout: QVBoxLayout) -> None:
        hButtonLayout = QHBoxLayout()
        hButtonLayout.addStretch(1)

        self.buttonSave.clicked.connect(self.onClickSaveAction)
        hButtonLayout.addWidget(self.buttonSave)

        hButtonLayout.addWidget(self.buttonClose)

        principalLayout.addLayout(hButtonLayout)


    @pyqtSlot()
    def addFieldTitleAndValueLine(self) -> None:
        """
        :return:
        """
        lineEditWithFieldTitle = QLineEdit()
        self.gridLayFieldTitlesAndValuesStack.addWidget(lineEditWithFieldTitle, self.fieldTitlesLineCounter, 0)

        lineEditWithFieldValue = self.getLineEditWithFieldValue()
        self.gridLayFieldTitlesAndValuesStack.addWidget(lineEditWithFieldValue, self.fieldTitlesLineCounter, 1)

        dictWithFieldTitleAndValue = {"lineEditWithFieldTitle": lineEditWithFieldTitle,
                                      "lineEditWithFieldValue": lineEditWithFieldValue}
        self.listOfWidgetsWithFieldTitlesAndValues.append(dictWithFieldTitleAndValue)

        self.fieldTitlesLineCounter += 1


    @pyqtSlot()
    def addNamedComboBoxLine(self) -> None:
        """
        :return:
        """
        comboBoxForChoosingNamedMsg = self.getComboBoxWithNamedMsg()
        self.comboBoxList.append(comboBoxForChoosingNamedMsg)
        buttonAddNamedMsg = self.getButtonAddComboBoxLine()

        responsesAndComboBoxesLimit = 20
        if self.comboBoxLineCounter <= responsesAndComboBoxesLimit:
            self.gridLayFewNamedMsgComboBoxStack.addWidget(comboBoxForChoosingNamedMsg, self.comboBoxLineCounter, 0)
        if self.comboBoxLineCounter == 0:
            # add button only on the first line
            self.gridLayFewNamedMsgComboBoxStack.addWidget(buttonAddNamedMsg, self.comboBoxLineCounter, 1)

        self.comboBoxLineCounter += 1


    @pyqtSlot()
    def switchActionEditors(self) -> None:
        """
        :return:
        """
        self.stackedWidgetsForDifferentActionTypes.setCurrentIndex(self.actionTypesList.currentIndex().row())


    @pyqtSlot()
    def onClickSaveAction(self) -> None:
        """
        :return:
        """

        if self.userEnteredDataIsValid():
            newActionDict = self.getEnteredActionDict()

            self.managerAutoresp.addAction(newActionDict)

            actionTitle = self.lineEditActionTitle.text()
            self.showSuccessMessageBox(_('Action \"') + actionTitle + _('\" saved.'))

            self.signalNewActionCreated.emit(newActionDict)


    def userEnteredDataIsValid(self) -> bool:
        if self.actionTitleIsNotUnique():
            return False

        if self.emptyActionTitle():
            return False

        if self.noMessageSelectedAsResponse():
            return False

        if self.noFieldTitlesOrValuesEnteredToAssigneNewValuesTo():
            return False

        return True


    def noFieldTitlesOrValuesEnteredToAssigneNewValuesTo(self):
        if self.getCurrentActionType() == 'Change some fields values and respond with the same msg':
            for widgetsLine in self.listOfWidgetsWithFieldTitlesAndValues:
                if widgetsLine["lineEditWithFieldTitle"].text() == "" or \
                   widgetsLine["lineEditWithFieldValue"].text() == '':
                    self.showErrorMessageBox(_('No field titles or values'),
                                             _('Enter field title and value'))
                    return True

        return False


    def noMessageSelectedAsResponse(self):
        if self.getCurrentActionType() == 'Respond with named msg' and \
                self.comboBoxForChoosingSingleNamedMsg.currentText() == '':
            self.showErrorMessageBox(_('No messaged selected'),
                                     _('Pick at least one msg from the list'))
            return True

        if self.getCurrentActionType() == 'Respond with few named msg':
            if all([self.noMessageSelectedInComboBox(combo) for combo in self.comboBoxList]):
                self.showErrorMessageBox(_('No messages selected to respond with'),
                                         _('Pick at least one msg from the list'))
                return True

        return False


    def emptyActionTitle(self) -> bool:
        actionTitle = self.lineEditActionTitle.text()
        if actionTitle == '':
            self.showErrorMessageBox(_('Empty action title!'),
                                     _('Enter action title'))
            return True
        else:
            return False


    def getStrOrderedActionTitlesList(self) -> str:
        allActionTitlesList = self.managerAutoresp.getAllActionTitlesList()
        stringHandler = handlerString.HandlerString()
        strActionTitlesList = stringHandler.getStrOrderedListFromList(allActionTitlesList)

        return strActionTitlesList


    def actionTitleIsNotUnique(self) -> bool:
        actionTitle = self.lineEditActionTitle.text()

        allActionTitlesList = self.managerAutoresp.getAllActionTitlesList()

        if actionTitle in allActionTitlesList:
            strActionTitlesList = self.getStrOrderedActionTitlesList()

            self.showErrorMessageBox(_('Action title is already in use!'),
                                     _('Enter unique action title. Action titles that are already in use:\n') +
                                     strActionTitlesList)
            return True
        else:
            return False


    def noMessageSelectedInComboBox(self, comboBox: QComboBox) -> bool:
        if comboBox.currentText() == '':
            return True
        else:
            return False


    def getEnteredActionDict(self) -> dict:
        """

        :return:
        """
        currentTypeIndex = self.actionTypesList.currentIndex().row()

        if currentTypeIndex == ROW_INDEX_OF_ACTION_TYPE_CHANGE_MODE:
            actionDict = self.getActionDictForActionTypeChangeMode()

        elif currentTypeIndex == ROW_INDEX_OF_ACTION_TYPE_RESPOND_WITH_RECEIVED_MSG_WITH_ASSIGNING_FIELDS:
            actionDict = self.getActionDictForActionTypeRespondWithReceivedMsgWithAssigningFields()

        elif currentTypeIndex == ROW_INDEX_OF_ACTION_TYPE_RESPOND_WITH_NAMED_MSG:
            actionDict = self.getActionDictForActionTypeRespondWithNamedMsg()

        elif currentTypeIndex == ROW_INDEX_OF_ACTION_TYPE_RESPOND_WITH_FEW_NAMED_MSG:
            actionDict = self.getActionDictForActionTypeRespondWithFewNamedMsg()
        else:
            actionDict = dict()

        return actionDict


    def getActionDictForActionTypeRespondWithFewNamedMsg(self) -> dict:
        actionDict = {"actionTitle": self.lineEditActionTitle.text(),
                      "actionType": 'actionTypeRespondWithFewNamedMsg',
                      "listOfMsgToRespondWith": self.getListOfMsgTitlesToRespondWith()}
        return actionDict


    def getActionDictForActionTypeRespondWithNamedMsg(self) -> dict:
        actionDict = {"actionTitle": self.lineEditActionTitle.text(),
                      "actionType": 'actionTypeRespondWithNamedMsg',
                      "listOfMsgToRespondWith": self.getListOfMsgTitlesToRespondWith()}
        return actionDict


    def getActionDictForActionTypeRespondWithReceivedMsgWithAssigningFields(self) -> dict:
        actionDict = {"actionTitle": self.lineEditActionTitle.text(),
                      "actionType": 'actionTypeRespondWithReceivedMsgWithAssigningFields',
                      "listOfFieldTitlesAndValuesToReplaceWhenRespondingWithReceivedMsg":
                          self.getListOfFieldTitlesAndValuesToReplaceWhenRespondingWithReceivedMsg()}
        return actionDict


    def getActionDictForActionTypeChangeMode(self) -> dict:
        actionDict = {"actionTitle": self.lineEditActionTitle.text(),
                      "actionType": 'actionTypeChangeMode',
                      "newMode": self.comboBoxForChoosingModes.currentText()}
        return actionDict


    def getCurrentActionType(self) -> str:
        """

        :return:
        """
        currentTypeIndex = self.actionTypesList.currentIndex().row()

        if currentTypeIndex == ROW_INDEX_OF_ACTION_TYPE_CHANGE_MODE:
            return 'actionTypeChangeMode'
        elif currentTypeIndex == ROW_INDEX_OF_ACTION_TYPE_RESPOND_WITH_RECEIVED_MSG_WITH_ASSIGNING_FIELDS:
            return 'actionTypeRespondWithReceivedMsgWithAssigningFields'
        elif currentTypeIndex == ROW_INDEX_OF_ACTION_TYPE_RESPOND_WITH_NAMED_MSG:
            return 'actionTypeRespondWithNamedMsg'
        elif currentTypeIndex == ROW_INDEX_OF_ACTION_TYPE_RESPOND_WITH_FEW_NAMED_MSG:
            return 'actionTypeRespondWithFewNamedMsg'
        else:
            return 'actionTypeUnknown'


    def getListOfMsgTitlesToRespondWith(self) -> list:
        """

        :return:
        """
        msgTitlesToRespondWithList = []

        currentActionType = self.getCurrentActionType()

        if currentActionType == 'actionTypeRespondWithNamedMsg':
            msgTitle = self.comboBoxForChoosingSingleNamedMsg.currentText()
            msgTitlesToRespondWithList.append(msgTitle)
        elif currentActionType == 'actionTypeRespondWithFewNamedMsg':
            msgTitlesToRespondWithList = [combo.currentText() for combo in self.comboBoxList]

        msgTitlesToRespondWithList = list(filter(lambda msgTitle: msgTitle != '', msgTitlesToRespondWithList))

        return msgTitlesToRespondWithList


    def getListOfFieldTitlesAndValuesToReplaceWhenRespondingWithReceivedMsg(self) -> list:
        """

        :return:
        """
        listOfFieldTitlesAndValues = []

        for widgetPairForField in self.listOfWidgetsWithFieldTitlesAndValues:
            if widgetPairForField["lineEditWithFieldTitle"].text() != '' and \
               widgetPairForField["lineEditWithFieldValue"].text() != '':
                fieldTitle = widgetPairForField["lineEditWithFieldTitle"].text()
                fieldValue = widgetPairForField["lineEditWithFieldValue"].text()

                dictWithFieldTitleAndValue = {"fieldTitle": fieldTitle,
                                              "fieldValue": fieldValue}

                listOfFieldTitlesAndValues.append(dictWithFieldTitleAndValue)

        return listOfFieldTitlesAndValues


    def getHexOfNamedMsg(self, msgTitle: str) -> str:
        """
        :param msgTitle:
        :return:
        """
        namedMsgHexStr = self.managerNamedMsg.getHexStrByMsgTitle(msgTitle)

        return namedMsgHexStr


    @pyqtSlot()
    def createNewNamedMsg(self) -> None:
        """

        :return:
        """
        window = windowNamedMsgEditor.WindowNamedMsgEditor(self.profileTitle)
        window.signalNamedMsgAdded.connect(self.addNewNamedMsg)
        window.exec_()


    @pyqtSlot(dict)
    def addNewNamedMsg(self, dictForNewNamedMsg: dict) -> None:
        """

        :param dictForNewNamedMsg:
        :return:
        """
        msgTitle = dictForNewNamedMsg["msgTitle"]

        self.comboBoxForChoosingSingleNamedMsg.addItem(msgTitle)

        for comboBox in self.comboBoxList:
            comboBox.addItem(msgTitle)

        self.managerNamedMsg.readNamedMsgsFromFile()
