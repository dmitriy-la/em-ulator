import gettext

from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QComboBox, QGridLayout, QGroupBox, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QLayout, QLineEdit, QPushButton
from PyQt5.QtWidgets import QSpinBox, QStackedWidget, QVBoxLayout

import src.handlers.handlerString as handlerString
import src.managers.managerAutoresponseSettings as managerAutoresponseSettings
import src.managers.managerNamedMsg as managerNamedMsg
import src.managers.managerNamedRegexp as managerNamedRegexp
import src.ui.windows.windowNamedMsgEditor as windowNamedMsgEditor
import src.ui.windows.windowNamedRegexpEditor as windowNamedRegexpEditor
import src.ui.windows.windowProfiledWindow as windowProfiledWindow


_ = gettext.gettext


INDEX_OF_CONDITION_TYPE_TIME_PASSED_AFTER_START = 0
INDEX_OF_CONDITION_TYPE_RECEIVED_SINGLE_MSG = 1
INDEX_OF_CONDITION_TYPE_RECEIVED_FEW_MSG = 2
INDEX_OF_CONDITION_TYPE_TIME_PASSED_AFTER_RECEIVING_MSG = 3
INDEX_OF_CONDITION_TYPE_TIME_PASSED_AFTER_SENDING_MSG = 4
INDEX_OF_CONDITION_TYPE_COMPOSITE_CONDITION = 5


class WindowAutorespConditionEditor(windowProfiledWindow.WindowProfiledWindow):
    signalNewCondCreated = pyqtSignal(dict)

    def __init__(self, profileTitle: str, condTitleToEdit='', parent=None):
        super().__init__(profileTitle, parent)
        self.condTitleToEdit = condTitleToEdit

        self.comboBoxFewMsgRegexpList = []
        self.comboBoxLineCounter = 0

        self.comboBoxCondList = []
        self.comboBoxCondLineCounter = 0

        self.managerNamedMsg = managerNamedMsg.ManagerNamedMsg(self.profileTitle)

        self.managerNamedRegexp = managerNamedRegexp.ManagerNamedRegexp(self.profileTitle)

        self.managerAutorespSettings = managerAutoresponseSettings.ManagerAutoresponseSettings(self.profileTitle)

        self.initUI()


    def initUI(self) -> None:
        self.setWindowProperties()

        principalLayout = QVBoxLayout(self)
        self.addLabelConditionTitle(principalLayout)
        self.addLineEditCondTitle(principalLayout)

        self.addLabelCondType(principalLayout)
        self.addComboBoxWithCondTypesAndStackedWidgetsForAllCondTypes(principalLayout)

        self.addButtonsSaveAndClose(principalLayout)

        self.show()


    def setWindowProperties(self) -> None:
        """

        :return:
        """
        self.title = _('Condition Editor')
        self.setWindowTitle(self.title)

        self.setGeometry(500, 200, 300, 400)

        self.setFocusPolicy(Qt.ClickFocus)
        self.setModal(True)


    def addLabelConditionTitle(self, principalLayout: QVBoxLayout) -> None:
        labelConditionTitle = QLabel(_('Condition title:'))
        principalLayout.addWidget(labelConditionTitle)


    def addLineEditCondTitle(self, principalLayout: QVBoxLayout) -> None:
        self.lineEditCondTitle = QLineEdit(self)
        principalLayout.addWidget(self.lineEditCondTitle)


    def addLabelCondType(self, principalLayout: QVBoxLayout) -> None:
        labelCondType = QLabel(_('Condition type:'))
        principalLayout.addWidget(labelCondType)


    def addComboBoxWithCondTypesAndStackedWidgetsForAllCondTypes(self, principalLayout: QVBoxLayout) -> None:
        vLay = QVBoxLayout(self)

        self.addComboBoxCondTypes(vLay)
        self.addStackedWidgetsForDifferentCondTypes(vLay)

        principalLayout.addLayout(vLay)


    def addComboBoxCondTypes(self, vLay: QVBoxLayout) -> None:
        """

        :param vLay:
        :return:
        """
        self.comboBoxCondTypes = QComboBox(self)

        condTypes = ['', '', '', '', '', '']
        condTypes[INDEX_OF_CONDITION_TYPE_TIME_PASSED_AFTER_START] = _('Time passed after start, ms')
        condTypes[INDEX_OF_CONDITION_TYPE_RECEIVED_SINGLE_MSG] = _('MSG received')
        condTypes[INDEX_OF_CONDITION_TYPE_RECEIVED_FEW_MSG] = _('Few MSG received')
        condTypes[INDEX_OF_CONDITION_TYPE_TIME_PASSED_AFTER_RECEIVING_MSG] = _('Time passed after receiving MSG, ms')
        condTypes[INDEX_OF_CONDITION_TYPE_TIME_PASSED_AFTER_SENDING_MSG] = _('Time passed after sending MSG, ms')
        condTypes[INDEX_OF_CONDITION_TYPE_COMPOSITE_CONDITION] = _('Composite condition from previously created conditions')

        self.comboBoxCondTypes.addItems(condTypes)
        self.comboBoxCondTypes.setCurrentIndex(0)

        self.comboBoxCondTypes.currentIndexChanged.connect(self.switchCondEditors)

        vLay.addWidget(self.comboBoxCondTypes)


    def addStackedWidgetsForDifferentCondTypes(self, vLay: QVBoxLayout) -> None:
        """

        :param vLay:
        :return:
        """
        self.stackedWidgetsForCondTypes = QStackedWidget(self)

        groupBoxForCondTypeTimePassedAfterStart = self.getGroupBoxForCondTypeTimePassedAfterStart()
        self.stackedWidgetsForCondTypes.insertWidget(INDEX_OF_CONDITION_TYPE_TIME_PASSED_AFTER_START,
                                                     groupBoxForCondTypeTimePassedAfterStart)

        groupBoxForCondTypeSingleMsgReceived = self.getGroupBoxForCondTypeSingleMsgReceived()
        self.stackedWidgetsForCondTypes.insertWidget(INDEX_OF_CONDITION_TYPE_RECEIVED_SINGLE_MSG,
                                                     groupBoxForCondTypeSingleMsgReceived)

        groupBoxForCondTypeFewMsgReceived = self.getGroupBoxForCondTypeFewMsgReceived()
        self.stackedWidgetsForCondTypes.insertWidget(INDEX_OF_CONDITION_TYPE_RECEIVED_FEW_MSG,
                                                     groupBoxForCondTypeFewMsgReceived)

        groupBoxForCondTypeTimePassedAfterReceiveMsg = self.getGroupBoxForCondTypeTimePassedAfterReceiveMsg()
        insertArgs = [INDEX_OF_CONDITION_TYPE_TIME_PASSED_AFTER_RECEIVING_MSG,
                      groupBoxForCondTypeTimePassedAfterReceiveMsg]
        self.stackedWidgetsForCondTypes.insertWidget(*insertArgs)

        groupBoxForCondTypeTimePassedAfterSendMsg = self.getGroupBoxForCondTypeTimePassedAfterSendMsg()
        insertArgs = [INDEX_OF_CONDITION_TYPE_TIME_PASSED_AFTER_SENDING_MSG, groupBoxForCondTypeTimePassedAfterSendMsg]
        self.stackedWidgetsForCondTypes.insertWidget(*insertArgs)

        groupBoxForCondTypeCompositeConditions = self.getGroupBoxForForCondTypeCompositeConditions()
        self.stackedWidgetsForCondTypes.insertWidget(INDEX_OF_CONDITION_TYPE_COMPOSITE_CONDITION,
                                                     groupBoxForCondTypeCompositeConditions)

        vLay.addWidget(self.stackedWidgetsForCondTypes)


    def getGroupBoxForCondTypeTimePassedAfterStart(self) -> QGroupBox:
        """

        :return:
        """
        comboGroup = QGroupBox()

        hLaySpinBox = self.getHorLayoutWithSpinBox()

        vLaySpinBox = QVBoxLayout()
        vLaySpinBox.addLayout(hLaySpinBox)
        vLaySpinBox.addStretch()

        comboGroup.setLayout(vLaySpinBox)

        return comboGroup


    def getGroupBoxForCondTypeTimePassedAfterReceiveMsg(self) -> QGroupBox:
        """

        :return:
        """
        comboGroup = QGroupBox()

        hLaySpinBox = self.getHorLayoutWithSpinBox()

        self.comboBoxForChoosingSingleNamedRegexpWithPassedTime = self.getComboBoxWithNamedRegexp()
        hLaySpinBox.addWidget(QLabel(_('after receiving msg:')))
        hLaySpinBox.addWidget(self.comboBoxForChoosingSingleNamedRegexpWithPassedTime)
        hLaySpinBox.addStretch(1)

        vLaySpinBox = QVBoxLayout()
        vLaySpinBox.addLayout(hLaySpinBox)
        vLaySpinBox.addStretch()

        self.addButtonForCreatingNewNamedRegexp(vLaySpinBox)

        comboGroup.setLayout(vLaySpinBox)

        return comboGroup


    def getHorLayoutWithSpinBox(self) -> QHBoxLayout:
        """

        :return:
        """
        spinBox = QSpinBox()
        spinBox.setRange(0, 99999999)

        hLaySpinBox = QHBoxLayout()
        hLaySpinBox.addWidget(spinBox)

        labelMs = QLabel(_('ms'))
        hLaySpinBox.addWidget(labelMs)

        return hLaySpinBox


    def getGroupBoxForCondTypeTimePassedAfterSendMsg(self) -> QGroupBox:
        """

        :return:
        """
        comboGroup = QGroupBox()

        hLaySpinBox = self.getHorLayoutWithSpinBox()

        self.comboBoxForChoosingSingleNamedMsg = self.getComboBoxWithNamedMsg()
        hLaySpinBox.addWidget(QLabel(_('after sending msg:')))
        hLaySpinBox.addWidget(self.comboBoxForChoosingSingleNamedMsg)
        hLaySpinBox.addStretch(1)

        vLaySpinBox = QVBoxLayout()
        vLaySpinBox.addLayout(hLaySpinBox)
        vLaySpinBox.addStretch()

        self.addButtonForCreatingNewNamedMsg(vLaySpinBox)

        comboGroup.setLayout(vLaySpinBox)

        return comboGroup


    def addButtonForCreatingNewNamedMsg(self, layout: QLayout) -> QPushButton:
        buttonForCreatingNewNamedMsg = QPushButton(_('+ Create msg'))
        buttonForCreatingNewNamedMsg.clicked.connect(self.createNewNamedMsg)
        layout.addWidget(buttonForCreatingNewNamedMsg)

        return buttonForCreatingNewNamedMsg


    def getComboBoxWithNamedMsg(self) -> QComboBox:
        """

        :return:
        """

        namedMsgsList = self.managerNamedMsg.getAllNamedMsgTitlesList()
        print(namedMsgsList)

        comboBoxForChoosingNamedMsg = QComboBox()

        comboBoxForChoosingNamedMsg.addItem('')
        comboBoxForChoosingNamedMsg.addItems(namedMsgsList)

        return comboBoxForChoosingNamedMsg


    def getGroupBoxForCondTypeFewMsgReceived(self) -> QGroupBox:
        """

        :return:
        """
        comboGroup = QGroupBox()

        self.gridLayComboBoxStack = self.getGridLayComboBoxStack()

        vLayForGrid = QVBoxLayout(self)
        vLayForGrid.addLayout(self.gridLayComboBoxStack)
        vLayForGrid.addStretch()

        self.buttonForCreatingNewNamedRegexp = self.addButtonForCreatingNewNamedRegexp(vLayForGrid)

        comboGroup.setLayout(vLayForGrid)

        self.comboBoxLineCounter += 1

        return comboGroup


    def getGridLayComboBoxStack(self) -> QGridLayout:
        gridLayComboBoxStack = QGridLayout(self)

        comboBoxForChoosingNamedMsg = self.getComboBoxWithNamedRegexp()
        self.comboBoxFewMsgRegexpList.append(comboBoxForChoosingNamedMsg)
        gridLayComboBoxStack.addWidget(comboBoxForChoosingNamedMsg, 0, 0)

        buttonAddNamedMsg = self.getButtonAddComboBoxLine()
        gridLayComboBoxStack.addWidget(buttonAddNamedMsg, 0, 1)

        return gridLayComboBoxStack


    def addButtonForCreatingNewNamedRegexp(self, layout: QLayout) -> QPushButton:
        buttonForCreatingNewNamedRegexp = QPushButton(_('+ Create regexp'))
        buttonForCreatingNewNamedRegexp.clicked.connect(self.createNewNamedRegexp)
        layout.addWidget(buttonForCreatingNewNamedRegexp)

        return buttonForCreatingNewNamedRegexp


    def getComboBoxWithNamedRegexp(self) -> QComboBox:
        """

        :return:
        """
        namedMsgsList = self.managerNamedRegexp.getAllNamedRegexpTitlesList()
        print("Combo named regexp, namedMsgsList", namedMsgsList)
        comboBoxForChoosingNamedRegexp = QComboBox()

        comboBoxForChoosingNamedRegexp.addItem('')
        comboBoxForChoosingNamedRegexp.addItems(namedMsgsList)

        return comboBoxForChoosingNamedRegexp


    def getButtonAddComboBoxLine(self) -> QPushButton:
        """

        :return:
        """
        buttonAddNamedMsg = QPushButton('+')
        buttonAddNamedMsg.setMaximumWidth(25)
        buttonAddNamedMsg.clicked.connect(self.addNamedComboBoxLine)

        return buttonAddNamedMsg


    def getGroupBoxForCondTypeSingleMsgReceived(self) -> QGroupBox:
        """

        :return:
        """
        comboGroup = QGroupBox()

        vLaySingleComboBox = QVBoxLayout()

        self.comboBoxForChoosingSingleNamedRegexp = self.getComboBoxWithNamedRegexp()

        vLaySingleComboBox.addWidget(self.comboBoxForChoosingSingleNamedRegexp)

        vLaySingleComboBox.addStretch()

        self.addButtonForCreatingNewNamedRegexp(vLaySingleComboBox)

        comboGroup.setLayout(vLaySingleComboBox)

        return comboGroup


    def getGroupBoxForForCondTypeCompositeConditions(self) -> QGroupBox:
        """

        :return:
        """
        comboGroup = QGroupBox()

        comboBoxWithConditionTitles = self.getComboBoxWithConditionTitles()

        self.gridLayComboBoxConditionStack = QGridLayout(self)

        self.gridLayComboBoxConditionStack.addWidget(comboBoxWithConditionTitles, 0, 0)

        buttonAddCondLine = self.getButtonAddConditionLine()
        self.gridLayComboBoxConditionStack.addWidget(buttonAddCondLine, 0, 1)

        vLayForGrid = QVBoxLayout(self)
        vLayForGrid.addLayout(self.gridLayComboBoxConditionStack)
        vLayForGrid.addStretch()

        comboGroup.setLayout(vLayForGrid)

        self.comboBoxCondList.append(comboBoxWithConditionTitles)
        self.comboBoxCondLineCounter += 1

        return comboGroup


    def getComboBoxWithConditionTitles(self) -> QComboBox:
        """

        :return:
        """
        condList = self.managerAutorespSettings.getConditionList()

        comboBoxWithConditionTitles = QComboBox()

        comboBoxWithConditionTitles.addItem('')
        for cond in condList:
            comboBoxWithConditionTitles.addItem(cond['condTitle'])

        return comboBoxWithConditionTitles


    def getButtonAddConditionLine(self) -> QPushButton:
        """

        :return:
        """
        buttonAddNamedMsg = QPushButton('+')
        buttonAddNamedMsg.setMaximumWidth(25)
        buttonAddNamedMsg.clicked.connect(self.addConditionLine)

        return buttonAddNamedMsg


    def addButtonsSaveAndClose(self, principalLayout: QVBoxLayout) -> None:
        """

        :return:
        """
        hLayoutButtonsSaveAndClose = QHBoxLayout()
        hLayoutButtonsSaveAndClose.addStretch(1)

        self.buttonSave.setText(_('Save condition'))
        self.buttonSave.clicked.connect(self.onClickSaveCondition)
        hLayoutButtonsSaveAndClose.addWidget(self.buttonSave)

        hLayoutButtonsSaveAndClose.addWidget(self.buttonClose)

        principalLayout.addLayout(hLayoutButtonsSaveAndClose)


    @pyqtSlot()
    def addConditionLine(self) -> None:
        """

        :return:
        """
        comboBoxWithCondition = self.getComboBoxWithConditionTitles()
        self.comboBoxCondList.append(comboBoxWithCondition)

        self.gridLayComboBoxConditionStack.addWidget(comboBoxWithCondition, self.comboBoxCondLineCounter, 0)

        self.comboBoxCondLineCounter += 1


    @pyqtSlot()
    def addNamedComboBoxLine(self) -> None:
        """

        :return:
        """
        comboBoxForChoosingNamedRegexp = self.getComboBoxWithNamedRegexp()
        self.comboBoxFewMsgRegexpList.append(comboBoxForChoosingNamedRegexp)
        buttonAddNamedRegexp = self.getButtonAddComboBoxLine()

        conditionsAndComboBoxesLimit = 100
        if self.comboBoxLineCounter <= conditionsAndComboBoxesLimit:
            self.gridLayComboBoxStack.addWidget(comboBoxForChoosingNamedRegexp, self.comboBoxLineCounter, 0)
        if self.comboBoxLineCounter == 0:
            self.gridLayComboBoxStack.addWidget(buttonAddNamedRegexp, self.comboBoxLineCounter, 1)

        self.comboBoxLineCounter += 1


    @pyqtSlot()
    def switchCondEditors(self) -> None:
        self.stackedWidgetsForCondTypes.setCurrentIndex(self.comboBoxCondTypes.currentIndex())


    @pyqtSlot()
    def onClickSaveCondition(self) -> None:
        """

        :return:
        """
        condTitle = self.lineEditCondTitle.text()
        noTitleEnteredForCondition = (condTitle == '')
        if noTitleEnteredForCondition:
            self.showErrorMessageBox(_('No title for condition'), _('Enter condition title'))
            return
        if self.conditionTitleIsNotUnique(condTitle):
            return
        if self.getCurrentCondType() == 'condTypeReceivedFewMsg':
            if self.noMsgsSelectedForCondition():
                self.showErrorMessageBox(_('No message selected'), _('Select at least one msg from the list'))
                return

        newConditionDict = self.getEnteredConditionDict()

        for combo in self.comboBoxCondList:
            combo.addItem(newConditionDict['condTitle'])

        self.managerAutorespSettings.addCondition(newConditionDict)

        self.signalNewCondCreated.emit(newConditionDict)

        self.showSuccessMessageBox(_('Condition \"') + self.lineEditCondTitle.text() + _('\" saved.'))


    def conditionTitleIsNotUnique(self, condTitle: str) -> bool:
        allConditionTitlesList = self.managerAutorespSettings.getAllConditionTitlesList()

        if condTitle in allConditionTitlesList:
            stringHandler = handlerString.HandlerString()
            strCondTitlesList = stringHandler.getStrOrderedListFromList(allConditionTitlesList)

            self.showErrorMessageBox(_('Condition title is already in use!'),
                                     _('Enter unique condition title. Condition titles that are already in use:\n') +
                                     strCondTitlesList)
            return True
        else:
            return False


    def noMsgsSelectedForCondition(self) -> bool:
        """

        :return:
        """
        emptyComboCounter = 0
        for combo in self.comboBoxFewMsgRegexpList:
            if combo.currentText() == '':
                emptyComboCounter += 1

        if emptyComboCounter == len(self.comboBoxFewMsgRegexpList):
            return True
        else:
            return False


    def getEnteredConditionDict(self) -> dict:
        """

        :return:
        """
        currentTypeIndex = self.comboBoxCondTypes.currentIndex()

        if currentTypeIndex == INDEX_OF_CONDITION_TYPE_TIME_PASSED_AFTER_START:
            conditionDict = self.getCondDictForCondTypeTimePassedAfterStart()
        elif (currentTypeIndex == INDEX_OF_CONDITION_TYPE_RECEIVED_SINGLE_MSG or
              currentTypeIndex == INDEX_OF_CONDITION_TYPE_RECEIVED_FEW_MSG):
            conditionDict = self.getCondDictForCondTypeReceivedOneOrFewMsg()
        elif (currentTypeIndex == INDEX_OF_CONDITION_TYPE_TIME_PASSED_AFTER_RECEIVING_MSG or
              currentTypeIndex == INDEX_OF_CONDITION_TYPE_TIME_PASSED_AFTER_SENDING_MSG):
            conditionDict = self.getCondDictForCondTypeTimePassedAfterSendOrReceive()
        elif currentTypeIndex == INDEX_OF_CONDITION_TYPE_COMPOSITE_CONDITION:
            conditionDict = self.getCondDictForCondTypeCompositeCondition()
        else:
            return dict()

        return conditionDict


    def getCondDictForCondTypeCompositeCondition(self) -> dict:
        conditionDict = {"condTitle": self.lineEditCondTitle.text(),
                         "condType": self.getCurrentCondType(),
                         "condTitlesList": self.getCondTitlesToConcatInCompositeCond()}
        return conditionDict


    def getCondDictForCondTypeTimePassedAfterSendOrReceive(self) -> dict:
        conditionDict = {"condTitle": self.lineEditCondTitle.text(),
                         "condType": self.getCurrentCondType(),
                         "condTimeMs": self.getTimePassedDataFromSpinBox(),
                         "condRegexpTitlesList": self.getCondRegexpTitlesList()}
        return conditionDict


    def getCondDictForCondTypeReceivedOneOrFewMsg(self) -> dict:
        conditionDict = {"condTitle": self.lineEditCondTitle.text(),
                         "condType": self.getCurrentCondType(),
                         "condRegexpTitlesList": self.getCondRegexpTitlesList()}
        return conditionDict


    def getCondDictForCondTypeTimePassedAfterStart(self) -> dict:
        return {"condTitle": self.lineEditCondTitle.text(),
                "condType": self.getCurrentCondType(),
                "condTimeMs": self.getTimePassedDataFromSpinBox()}


    def getTimePassedDataFromSpinBox(self) -> int:
        """

        :return:
        """
        currentTypeIndex = self.comboBoxCondTypes.currentIndex()

        if currentTypeIndex in range(6):
            curGroupBox = self.stackedWidgetsForCondTypes.currentWidget()

            for widget in curGroupBox.children():
                if isinstance(widget, QSpinBox):
                    return widget.value()
        return 0


    def getCondTitlesToConcatInCompositeCond(self) -> list:
        """
        """
        listOfCondTitlesInCompositeCond = []

        for combo in self.comboBoxCondList:
            if combo.currentText() != '':
                listOfCondTitlesInCompositeCond.append(combo.currentText())

        return listOfCondTitlesInCompositeCond


    def getCurrentCondType(self) -> str:
        """

        :return:
        """
        currentTypeIndex = self.comboBoxCondTypes.currentIndex()

        if currentTypeIndex == INDEX_OF_CONDITION_TYPE_TIME_PASSED_AFTER_START:
            return 'condTypeTimePassedAfterStart'
        elif currentTypeIndex == INDEX_OF_CONDITION_TYPE_RECEIVED_SINGLE_MSG:
            return 'condTypeReceivedSingleMsg'
        elif currentTypeIndex == INDEX_OF_CONDITION_TYPE_RECEIVED_FEW_MSG:
            return 'condTypeReceivedFewMsg'
        elif currentTypeIndex == INDEX_OF_CONDITION_TYPE_TIME_PASSED_AFTER_RECEIVING_MSG:
            return 'condTypeTimePassedAfterReceivingMsg'
        elif currentTypeIndex == INDEX_OF_CONDITION_TYPE_TIME_PASSED_AFTER_SENDING_MSG:
            return 'condTypeTimePassedAfterSendMsg'
        elif currentTypeIndex == INDEX_OF_CONDITION_TYPE_COMPOSITE_CONDITION:
            return 'condTypeCompositeCond'
        else:
            return 'condTypeUnknown'


    def getCondRegexpTitlesList(self) -> list:
        """

        :return:
        """
        condRegexpTitlesList = []

        currentCondType = self.getCurrentCondType()

        if currentCondType == 'condTypeReceivedFewMsg':
            condRegexpTitlesList = self.getRegexpTitlesListForCondTypeReceivedFewMsg()
        elif currentCondType == 'condTypeTimePassedAfterSendMsg':
            condRegexpTitlesList = self.getRegexpTitlesListForcondTypeTimePassedAfterSendMsg()
        elif currentCondType == 'condTypeTimePassedAfterReceivingMsg':
            condRegexpTitlesList = self.getRegexpTitlesListForCondTypeTimePassedAfterReceivingMsg()
        elif currentCondType == 'condTypeReceivedSingleMsg':
            condRegexpTitlesList = self.getRegexpTitlesListForCondTypeReceivedSingleMsg()

        return condRegexpTitlesList


    def getRegexpTitlesListForCondTypeReceivedSingleMsg(self) -> list:
        """

        :return:
        """
        condRegexpTitlesList = []
        regexpTitle = self.comboBoxForChoosingSingleNamedRegexp.currentText()

        if regexpTitle != '':
            condRegexpTitlesList.append(regexpTitle)

        return condRegexpTitlesList


    def getRegexpTitlesListForCondTypeTimePassedAfterReceivingMsg(self) -> list:
        """

        :return:
        """
        condRegexpTitlesList = []
        regexpTitle = self.comboBoxForChoosingSingleNamedRegexpWithPassedTime.currentText()

        if regexpTitle != '':
            condRegexpTitlesList.append(regexpTitle)

        return condRegexpTitlesList


    def getRegexpTitlesListForcondTypeTimePassedAfterSendMsg(self) -> list:
        """

        :return:
        """
        condRegexpTitlesList = []

        msgTitle = self.comboBoxForChoosingSingleNamedMsg.currentText()

        if msgTitle != '':
            condRegexpTitlesList.append(msgTitle)

        return condRegexpTitlesList


    def getNamedMsgByTitle(self, msgTitle: str) -> str:
        """

        :param msgTitle:
        :return:
        """
        namedMsgHexStr = self.managerNamedMsg.getHexStrByMsgTitle(msgTitle)

        return namedMsgHexStr


    def getRegexpTitlesListForCondTypeReceivedFewMsg(self) -> list:
        """

        :return:
        """
        condRegexpTitlesList = []

        for combo in self.comboBoxFewMsgRegexpList:
            msgRegexpTitle = combo.currentText()

            if msgRegexpTitle != '':
                condRegexpTitlesList.append(msgRegexpTitle)

        return condRegexpTitlesList


    def getBinRegexpFromRegexpTitle(self, regexpTitle: str) -> str:
        """

        :param regexpTitle:
        :return:
        """
        binRegexp = self.managerNamedRegexp.getBinRegexpFromRegexpTitle(regexpTitle)

        return binRegexp


    @pyqtSlot()
    def createNewNamedRegexp(self) -> None:
        regexpCreator = windowNamedRegexpEditor.WindowNamedRegexpEditor(self.profileTitle)
        regexpCreator.signalNamedRegexpAdded.connect(self.addNewNamedRegexp)
        regexpCreator.exec_()


    @pyqtSlot()
    def createNewNamedMsg(self) -> None:
        window = windowNamedMsgEditor.WindowNamedMsgEditor(self.profileTitle)
        window.signalNamedMsgAdded.connect(self.addNewNamedMsg)
        window.exec_()


    @pyqtSlot(dict)
    def addNewNamedMsg(self, namedMsgDict: dict) -> None:
        """
        :param namedMsgDict:
        :return:
        """
        namedMsgTitle = namedMsgDict["msgTitle"]

        self.managerNamedMsg.readNamedMsgsFromFile()

        self.comboBoxForChoosingSingleNamedMsg.addItem(namedMsgTitle)


    @pyqtSlot(str, str)
    def addNewNamedRegexp(self, title: str, binRegexp: str) -> None:
        """

        :param title:
        :param binRegexp:
        :return:
        """
        self.comboBoxForChoosingSingleNamedRegexp.addItem(title)

        curGroupBox = self.stackedWidgetsForCondTypes.currentWidget()

        for widget in curGroupBox.children():
            if isinstance(widget, QComboBox):
                widget.addItem(title)

        self.managerNamedRegexp.readNamedRegexpsFromFile()
