import gettext

from PyQt5.Qt import Qt
from PyQt5.QtCore import QSize, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAbstractItemView, QComboBox, QGroupBox
from PyQt5.QtWidgets import QHBoxLayout, QInputDialog, QLabel, QLineEdit
from PyQt5.QtWidgets import QListWidget, QMessageBox, QPushButton
from PyQt5.QtWidgets import QSplitter, QStackedWidget, QVBoxLayout

import src.handlers.handlerString as handlerString
import src.managers.managerAutoresponseSettings as managerAutoresponseSettings
import src.windows.windowAutorespActionEditor as windowAutorespActionEditor
import src.windows.windowAutorespConditionEditor as windowAutorespConditionEditor
import src.windows.windowProfiledWindow as windowProfiledWindow


_ = gettext.gettext


class WindowAutorespModesEditor(windowProfiledWindow.WindowProfiledWindow):
    def __init__(self, profileTitle: str, parent=None):
        super().__init__(profileTitle, parent)
        self.listConditionAndWidgetWithActions = []
        self.listModesAndWidgets = []

        self.managerAutorespSettings = managerAutoresponseSettings.ManagerAutoresponseSettings(self.profileTitle)

        self.listOfAllAutorespModes = self.managerAutorespSettings.getAllAutorespModesList()

        self.allCondList = self.managerAutorespSettings.getConditionList()

        self.allActionTitlesList = self.managerAutorespSettings.getAllActionTitlesList()

        self.initUI()

        self.dataForModeChanged = False


    def initUI(self) -> None:
        self.setWindowProperties()

        self.principalLayout = QHBoxLayout(self)
        self.principalSplitter = QSplitter(self)
        self.principalSplitter.setOrientation(Qt.Horizontal)

        self.comboBoxSelectModes = self.addComboBoxSelectModes()

        self.initLeftSideOfSplitter()
        self.initRightSideOfSplitter()

        self.initWholeWindow()

        self.show()


    def setWindowProperties(self) -> None:
        self.setMinimumWidth(800)

        self.title = _('Autoresponse Editor')
        self.setWindowTitle(self.title)

        self.xCoord = 300
        self.yCoord = 300
        self.height = 400
        self.width = 800
        self.setGeometry(self.xCoord, self.yCoord, self.width, self.height)

        self.setModal(True)
        self.setFocusPolicy(Qt.StrongFocus)


    def initWholeWindow(self) -> None:
        self.addCondForModeEditGroupBox()
        self.principalLayout.addWidget(self.principalSplitter)

        self.addGroupBoxActionsAssignedToCond()

        self.principalVertLayout = QVBoxLayout(self)
        vLayoutForButtonsCreateAndRemoveAction = self.addLayoutEnterProfileTitle()

        self.principalVertLayout.addLayout(vLayoutForButtonsCreateAndRemoveAction)
        self.principalVertLayout.addWidget(self.principalSplitter)

        self.addHLayoutForButtonsSaveAndCancel()
        self.principalLayout.addLayout(self.principalVertLayout)


    def initRightSideOfSplitter(self) -> None:
        self.hLayoutRight = QHBoxLayout(self)
        self.vLayoutLeft.setSpacing(0)
        self.hLayoutRight.addWidget(self.stackedWidgetsActionsToCond)

        self.addVLayoutForAddingActionsToCondition()

        self.hLayoutRight.addLayout(self.hLayoutForButtonsCreateAndDelCondition)


    def initLeftSideOfSplitter(self) -> None:
        self.vLayoutLeft = QHBoxLayout(self)
        self.stackedWidgetsActionsToCond = QStackedWidget(self)
        self.listWidgetConditions = self.addListWidgerConditions()
        self.fillAutorespModeInfoForCurrentMode()

        self.vLayoutLeft.addSpacing(5)
        self.hLayoutForButtonsCreateAndDelCondition = self.addHLayoutForButtonsCreateAndDelCondition()

        self.selectionModelConditions = self.listWidgetConditions.selectionModel()


    def addHLayoutForButtonsCreateAndDelCondition(self) -> QVBoxLayout:
        vLayoutForButtonsCreateAndDelCondition = QVBoxLayout()

        self.addButtonCreateNewCondition(vLayoutForButtonsCreateAndDelCondition)
        self.addButtonRemoveCond(vLayoutForButtonsCreateAndDelCondition)

        vLayoutForButtonsCreateAndDelCondition.addStretch(1)

        self.vLayoutLeft.addLayout(vLayoutForButtonsCreateAndDelCondition)

        return vLayoutForButtonsCreateAndDelCondition


    def addCondForModeEditGroupBox(self) -> None:
        self.condForModeEditGroupBox = QGroupBox(self)
        self.condForModeEditGroupBox.setTitle(_('Conditions:'))
        self.condForModeEditGroupBox.setLayout(self.vLayoutLeft)
        self.principalSplitter.addWidget(self.condForModeEditGroupBox)


    def addLayoutEnterProfileTitle(self) -> QHBoxLayout:
        self.layoutEnterProfileTitle = QHBoxLayout(self)
        self.addLabelSelectMode()
        self.layoutEnterProfileTitle.addWidget(self.comboBoxSelectModes)
        self.addButtonCreateNewAutorespMode()
        self.addButtonRemoveCurrentAutorespMode()
        self.layoutEnterProfileTitle.addStretch(1)

        vLayoutForButtonsCreateAndRemoveAction = self.addVLayoutForButtonsCreateAndRemoveAction()
        self.layoutEnterProfileTitle.addLayout(vLayoutForButtonsCreateAndRemoveAction)

        self.principalVertLayout.addLayout(self.layoutEnterProfileTitle)

        return vLayoutForButtonsCreateAndRemoveAction


    def addListWidgerConditions(self) -> QListWidget:
        listWidgetConditions = QListWidget(self)
        listWidgetConditions.setSelectionBehavior(QAbstractItemView.SelectRows)
        listWidgetConditions.currentRowChanged.connect(self.proccessCurrentCondChanged)
        self.vLayoutLeft.addWidget(listWidgetConditions)

        return listWidgetConditions


    def addButtonRemoveCond(self, hLayoutForButtonsSaveAndCancel: QVBoxLayout) -> None:
        buttonDelCond = QPushButton(self)
        buttonDelCond.setText('-')
        buttonDelCond.setMaximumWidth(26)
        buttonDelCond.setToolTip(_('Condition is removed for all modes'))

        buttonDelCond.clicked.connect(self.onClickRemoveCondition)

        hLayoutForButtonsSaveAndCancel.addWidget(buttonDelCond)


    def addButtonCreateNewCondition(self, hLayoutForButtonsSaveAndCancel: QVBoxLayout) -> None:
        buttonCreateNewCondition = QPushButton(self)

        buttonCreateNewCondition.setText('+')
        buttonCreateNewCondition.setMaximumWidth(26)
        buttonCreateNewCondition.setToolTip(_('Create new condition'))

        buttonCreateNewCondition.clicked.connect(self.onClickCreateNewCondition)

        hLayoutForButtonsSaveAndCancel.addWidget(buttonCreateNewCondition)


    def addVLayoutForAddingActionsToCondition(self) -> None:
        vLayoutForAddingActionsToCondition = QVBoxLayout()

        buttonAddActionToCond = QPushButton(self)
        buttonAddActionToCond.setMaximumWidth(26)
        buttonAddActionToCond.setText('+')
        buttonAddActionToCond.setToolTip(_('Add action triggered by condition'))
        buttonAddActionToCond.clicked.connect(self.addActionToCond)

        vLayoutForAddingActionsToCondition.addWidget(buttonAddActionToCond)
        vLayoutForAddingActionsToCondition.addStretch(1)

        self.hLayoutRight.addLayout(vLayoutForAddingActionsToCondition)


    def addGroupBoxActionsAssignedToCond(self) -> None:
        self.groupBoxActionsAssignedToCond = QGroupBox(self)

        self.groupBoxActionsAssignedToCond.setTitle(_('Actions to perform for selected condition:'))
        self.groupBoxActionsAssignedToCond.setLayout(self.hLayoutRight)

        self.principalSplitter.addWidget(self.groupBoxActionsAssignedToCond)


    def addHLayoutForButtonsSaveAndCancel(self) -> None:
        self.buttonSave.clicked.connect(self.onClickSaveAutorespMode)
        self.buttonClose.setText(_('Exit'))

        hLayoutForButtonsSaveAndCancel = QHBoxLayout()
        hLayoutForButtonsSaveAndCancel.addStretch(1)
        hLayoutForButtonsSaveAndCancel.setSpacing(0)

        hLayoutForButtonsSaveAndCancel.addWidget(self.buttonSave)
        hLayoutForButtonsSaveAndCancel.addWidget(self.buttonClose)

        self.principalVertLayout.addLayout(hLayoutForButtonsSaveAndCancel)


    def addVLayoutForButtonsCreateAndRemoveAction(self) -> QHBoxLayout:
        vLayoutForButtonsCreateAndRemoveAction = QHBoxLayout()

        buttonCreateNewAction = self.addButtonCreateNewAction()
        buttonRemoveAction = self.addButtonRemoveAction()

        vLayoutForButtonsCreateAndRemoveAction.addWidget(buttonCreateNewAction)
        vLayoutForButtonsCreateAndRemoveAction.addWidget(buttonRemoveAction)

        return vLayoutForButtonsCreateAndRemoveAction


    def addButtonRemoveAction(self) -> QPushButton:
        buttonRemoveAction = QPushButton(self)
        buttonRemoveAction.setText(_('Remove action'))

        pixmap = QPixmap('../icons/trash.png')
        saveIcon = QIcon(pixmap)
        buttonRemoveAction.setIcon(saveIcon)
        buttonRemoveAction.setIconSize(QSize(16, 16))

        buttonRemoveAction.clicked.connect(self.onClickRemoveAction)

        return buttonRemoveAction


    def addButtonCreateNewAction(self) -> QPushButton:
        buttonCreateNewAction = QPushButton(self)
        buttonCreateNewAction.setText(_('Create action'))

        pixmap = QPixmap('../icons/add-document.png')
        saveIcon = QIcon(pixmap)
        buttonCreateNewAction.setIcon(saveIcon)
        buttonCreateNewAction.setIconSize(QSize(16, 16))

        buttonCreateNewAction.clicked.connect(self.onClickCreateNewAction)

        return buttonCreateNewAction


    def addButtonRemoveCurrentAutorespMode(self) -> None:
        buttonRemoveCurrentAutorespMode = QPushButton(self)
        buttonRemoveCurrentAutorespMode.setText(_('-mode'))
        buttonRemoveCurrentAutorespMode.setMaximumWidth(43)

        buttonRemoveCurrentAutorespMode.clicked.connect(self.removeCurrentAutorespMode)

        self.layoutEnterProfileTitle.addWidget(buttonRemoveCurrentAutorespMode)


    def addButtonCreateNewAutorespMode(self) -> None:
        buttonCreateNewAutorespMode = QPushButton(self)
        buttonCreateNewAutorespMode.setText(_('+mode'))
        buttonCreateNewAutorespMode.setMaximumWidth(43)

        buttonCreateNewAutorespMode.clicked.connect(self.createNewAutorespMode)

        self.layoutEnterProfileTitle.addWidget(buttonCreateNewAutorespMode)


    def addLabelSelectMode(self) -> None:
        labelSelectMode = QLabel(self)
        labelSelectMode.setText(_('Select autoresponse mode:'))

        self.layoutEnterProfileTitle.addWidget(labelSelectMode)


    def addComboBoxSelectModes(self) -> QComboBox:
        comboBoxSelectModes = QComboBox(self)
        self.managerAutorespSettings = managerAutoresponseSettings.ManagerAutoresponseSettings(self.profileTitle)
        modesList = self.getAutorespModesList()
        comboBoxSelectModes.addItems(modesList)

        comboBoxSelectModes.setMinimumWidth(150)

        comboBoxSelectModes.currentTextChanged.connect(self.switchAutorespModes)

        return comboBoxSelectModes


    def getAutorespModesList(self) -> list:
        modeTitlesList = []

        for mode in self.listOfAllAutorespModes:
            modeTitlesList.append(mode['modeTitle'])

        if len(modeTitlesList) == 0:
            return ['initMode']
        else:
            return modeTitlesList


    @pyqtSlot()
    def switchAutorespModes(self) -> None:
        if self.dataForModeChanged:
            messageBoxArguments = ['', _('Unsaved changes for mode! Continue without save?'),
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes]

            userReply = QMessageBox.question(self, *messageBoxArguments)
            if userReply == QMessageBox.No:
                return

        self.listWidgetConditions.clear()
        self.listConditionAndWidgetWithActions.clear()

        self.clearStackedWidgets()

        self.fillAutorespModeInfoForCurrentMode()
        self.listWidgetConditions.setCurrentRow(0)

        self.dataForModeChanged = False


    def clearStackedWidgets(self) -> None:
        for i in range(self.stackedWidgetsActionsToCond.count()):
            widgetToRemove = self.stackedWidgetsActionsToCond.widget(i)
            self.stackedWidgetsActionsToCond.removeWidget(widgetToRemove)


    def fillAutorespModeInfoForCurrentMode(self) -> None:
        condList = self.managerAutorespSettings.getConditionList()

        self.listWidgetConditions.clear()
        self.listConditionAndWidgetWithActions.clear()

        for condIndex, cond in enumerate(condList):
            condTitle = cond['condTitle']
            self.listWidgetConditions.addItem(condTitle)

            listWidgetWithActions = self.getListWidgetWithActionsForCond(condTitle)

            condAndActionsDict = {"condTitle": condTitle, "listWidgetWithActions": listWidgetWithActions}
            self.listConditionAndWidgetWithActions.append(condAndActionsDict)

            self.stackedWidgetsActionsToCond.insertWidget(condIndex, listWidgetWithActions)


    @pyqtSlot()
    def createNewAutorespMode(self) -> None:
        newMode = self.getNewModeTitleFromInputDialog()

        newModeTitle = newMode[0]
        result = newMode[1]

        if result and self.modeTitleIsUnique(newModeTitle):
            self.comboBoxSelectModes.addItem(newModeTitle)
            self.comboBoxSelectModes.setCurrentText(newModeTitle)

            condAndActionsList = self.getCondAndActionsList()

            newModeDict = {'modeTitle': newModeTitle,
                           'condList':  condAndActionsList}

            self.listOfAllAutorespModes.append(newModeDict)

            self.managerAutorespSettings.updateModesList(self.listOfAllAutorespModes)

            self.fillAutorespModeInfoForCurrentMode()


    def getCondAndActionsList(self) -> list:
        condList = self.managerAutorespSettings.getConditionList()
        condAndActionsList = []

        for cond in condList:
            condAndActions = {'condTitle': cond['condTitle'], 'actionsAssignedToCond': []}
            condAndActionsList.append(condAndActions)

        return condAndActionsList


    def modeTitleIsUnique(self, modeTitle: str) -> bool:
        allModeTitlesList = self.managerAutorespSettings.getListOfAutorespModesTitles()

        if modeTitle in allModeTitlesList:
            stringHandler = handlerString.HandlerString()
            strModeTitlesList = stringHandler.getStrOrderedListFromList(allModeTitlesList)

            self.showErrorMessageBox(_('Mode title is already in use!'),
                                     _('Enter unique mode title. Mode titles that are already in use:\n') +
                                     strModeTitlesList)
            return False
        else:
            return True


    @pyqtSlot()
    def removeCurrentAutorespMode(self) -> None:
        curIndex = self.comboBoxSelectModes.currentIndex()
        modeTitleToDelete = self.comboBoxSelectModes.currentText()

        if modeTitleToDelete == 'initMode':
            self.showErrorMessageBox(_('initMode can\'t be removed, since it is used at the start up.'))
            return

        self.comboBoxSelectModes.removeItem(curIndex)

        self.listOfAllAutorespModes = list(filter(lambda mode: mode["modeTitle"] != modeTitleToDelete,
                                                  self.listOfAllAutorespModes))
        self.managerAutorespSettings.removeModeFromAutorespModesList(modeTitleToDelete)

        self.comboBoxSelectModes.setCurrentIndex(curIndex-1)


    def getNewModeTitleFromInputDialog(self) -> tuple:
        newModeTitleDialog = QInputDialog(self)
        newModeTitleDialog.setWindowTitle(_('Create new mode'))
        newModeTitleDialog.setLabelText(_('Enter new mode title'))

        newModeTitle = newModeTitleDialog.getText(QLineEdit(), _('Create new mode'), _('Enter new mode title'))

        return newModeTitle


    def getActionTitleToDeleteFromInputDialog(self) -> str:
        actionTitlesList = self.managerAutorespSettings.getAllActionTitlesList()

        inputDialogArguments = [_('Select action for removal'), _(" List of actions"), actionTitlesList, 0, False]

        item, result = QInputDialog.getItem(self, *inputDialogArguments)

        actionTitleToDelete = ''
        if result:
            actionTitleToDelete = item

        return actionTitleToDelete


    def getListWidgetWithActionsForCond(self, currentCondTitle: str) -> QListWidget:
        listWidget = QListWidget()
        listWidget.setUniformItemSizes(True)

        listOfActionsAssignedToCond = self.getListOfActionsAssignedToCond(currentCondTitle)

        for comboBoxIndex, action in enumerate(listOfActionsAssignedToCond):
            comboBox = self.getComboBoxWithActions()
            comboBox.setCurrentText(action)

            listWidget.addItem(action)

            listWidget.setItemWidget(listWidget.item(comboBoxIndex), comboBox)

        return listWidget


    def getListOfActionsAssignedToCond(self, condTitle: str) -> list:
        curModeTitle = self.comboBoxSelectModes.currentText()
        condList = self.getCondListOfMode(curModeTitle)

        listOfActionsAssignedToCond = []

        for cond in condList:
            if cond['condTitle'] == condTitle:
                listOfActionsAssignedToCond = cond['actionsAssignedToCond']
                break

        return listOfActionsAssignedToCond


    def getCondListOfMode(self, modeTitle: str) -> list:
        condList = []

        for mode in self.listOfAllAutorespModes:
            if mode['modeTitle'] == modeTitle:
                condList = mode['condList']
                break

        return condList


    @pyqtSlot()
    def proccessCurrentCondChanged(self) -> None:
        currentCondIndex = self.listWidgetConditions.currentRow()

        self.stackedWidgetsActionsToCond.setCurrentIndex(currentCondIndex)


    @pyqtSlot()
    def onClickRemoveCondition(self) -> None:
        curCondItem = self.listWidgetConditions.currentItem()
        condTitleToDelete = curCondItem.text()

        self.managerAutorespSettings.removeCondition(condTitleToDelete)

        curCondIndex = self.listWidgetConditions.currentRow()
        self.listWidgetConditions.takeItem(curCondIndex)

        listWidget = self.listConditionAndWidgetWithActions[curCondIndex]["listWidgetWithActions"]

        self.stackedWidgetsActionsToCond.removeWidget(listWidget)

        self.listConditionAndWidgetWithActions.remove(self.listConditionAndWidgetWithActions[curCondIndex])


    def addActionToCond(self) -> None:
        if len(self.listWidgetConditions) <= 0:
            return

        comboBoxAction = self.getComboBoxWithActions()
        curCondIndex = self.listWidgetConditions.currentIndex().row()

        currentListWidget = self.listConditionAndWidgetWithActions[curCondIndex]["listWidgetWithActions"]

        currentListWidget.addItem('')

        lastIndex = currentListWidget.count() - 1
        lastItem = currentListWidget.item(lastIndex)

        currentListWidget.setItemWidget(lastItem, comboBoxAction)


    def getComboBoxWithActions(self) -> QComboBox:
        comboBoxAction = QComboBox()
        comboBoxAction.setMinimumHeight(17)

        comboBoxAction.addItem('')
        # comboBoxAction.addItem(_('Save in separate log'))
        comboBoxAction.addItem(_('Respond with received msg'))
        # comboBoxAction.currentText()

        comboBoxAction.addItems(self.allActionTitlesList)

        comboBoxAction.currentIndexChanged.connect(self.markThatChangesToModeWereMade)

        return comboBoxAction


    @pyqtSlot()
    def markThatChangesToModeWereMade(self) -> None:
        self.dataForModeChanged = True


    @pyqtSlot()
    def onClickCreateNewCondition(self) -> None:
        windowCondEditor = windowAutorespConditionEditor.WindowAutorespConditionEditor(self.profileTitle)
        windowCondEditor.signalNewCondCreated.connect(self.addNewCondition)
        windowCondEditor.exec()


    @pyqtSlot()
    def onClickCreateNewAction(self) -> None:
        windowActionEditor = windowAutorespActionEditor.WindowAutorespActionEditor(self.profileTitle)
        windowActionEditor.signalNewActionCreated.connect(self.updateActionList)
        windowActionEditor.exec()


    @pyqtSlot()
    def onClickRemoveAction(self) -> None:
        actionTitleToRemove = self.getActionTitleToDeleteFromInputDialog()

        if actionTitleToRemove != '':
            self.managerAutorespSettings.removeAction(actionTitleToRemove)

            self.removeActionFromComboBoxes(actionTitleToRemove)

            self.allActionTitlesList.remove(actionTitleToRemove)

            self.showSuccessMessageBox(_("Action \"" + actionTitleToRemove + "\" removed."), '', "Remove")


    def removeActionFromComboBoxes(self, actionTitleToDelete: str) -> None:
        for conAndWidgetWithActions in self.listConditionAndWidgetWithActions:
            listWidget = conAndWidgetWithActions["listWidgetWithActions"]

            for listWidgetItemsIndex in range(listWidget.count()):
                item = listWidget.item(listWidgetItemsIndex)
                comboBox = listWidget.itemWidget(item)

                self.removeActionFromComboBox(actionTitleToDelete, comboBox)


    def removeActionFromComboBox(self, actionTitleToDelete: str, comboBox: QComboBox) -> None:
        if comboBox.currentText() == actionTitleToDelete:
            comboBox.setCurrentIndex(0)

        for comboBoxItemsIndex in range(comboBox.count()):
            if comboBox.itemText(comboBoxItemsIndex) == actionTitleToDelete:
                comboBox.removeItem(comboBoxItemsIndex)


    def removeActionFromCondition(self, actionTitleToDelete: str, condTitle: str) -> None:
        actionsList = self.getListOfActionsAssignedToCond(condTitle)

        for action in actionsList:
            if action == actionTitleToDelete:
                actionsList.remove(action)


    @pyqtSlot(dict)
    def addNewCondition(self, newCondDict: dict) -> None:
        newCondTitle = newCondDict['condTitle']
        listWidgetForNewCond = self.getListWidgetWithActionsForCond(newCondTitle)

        dictForNewCond = {'condTitle': newCondTitle,
                          'listWidgetWithActions': listWidgetForNewCond}

        self.listConditionAndWidgetWithActions.append(dictForNewCond)
        self.listWidgetConditions.addItem(newCondDict['condTitle'])

        listsCount = self.stackedWidgetsActionsToCond.count()
        self.stackedWidgetsActionsToCond.insertWidget(listsCount, listWidgetForNewCond)

        self.managerAutorespSettings.addCondition(newCondDict)


    @pyqtSlot(dict)
    def updateActionList(self, actionDict: dict) -> None:
        self.allActionTitlesList.append(actionDict['actionTitle'])

        self.managerAutorespSettings.readActionListFromFile()

        for dict in self.listConditionAndWidgetWithActions:
            listWidgetWithActions = dict["listWidgetWithActions"]
            actionCount = listWidgetWithActions.count()

            for i in range(actionCount):
                item = listWidgetWithActions.item(i)
                comboBox = listWidgetWithActions.itemWidget(item)
                comboBox.addItem(actionDict['actionTitle'])


    @pyqtSlot()
    def onClickSaveAutorespMode(self) -> None:
        newModeDict = self.getEnteredModeDict()

        oldModeIndex = -1
        for mode in self.listOfAllAutorespModes:
            if mode['modeTitle'] == self.comboBoxSelectModes.currentText():
                oldModeIndex = self.listOfAllAutorespModes.index(mode)
                self.listOfAllAutorespModes.pop(oldModeIndex)
                self.listOfAllAutorespModes.insert(oldModeIndex, newModeDict)
                break

        if oldModeIndex == -1:
            self.listOfAllAutorespModes.append(newModeDict)

        self.managerAutorespSettings.updateModesList(self.listOfAllAutorespModes)

        self.showSuccessMessageBox(_('Mode \"') + self.comboBoxSelectModes.currentText() + _('\" was saved.'))

        self.dataForModeChanged = False


    def getEnteredModeDict(self) -> dict:
        modeDict = {"modeTitle": self.comboBoxSelectModes.currentText(),
                    "condList": self.getCondAndAssignedActionsList()}

        return modeDict


    def getCondAndAssignedActionsList(self) -> list:
        condActionList = []

        for condAndWidgetWithActions in self.listConditionAndWidgetWithActions:
            condDict = self.getCondAndAssignedActionsDict(condAndWidgetWithActions)
            condActionList.append(condDict)

        return condActionList


    def getCondAndAssignedActionsDict(self, condAndWidgetWithActions: dict) -> dict:
        listWidget = condAndWidgetWithActions["listWidgetWithActions"]

        listActions = []

        for i in range(listWidget.count()):
            item = listWidget.item(i)
            comboBox = listWidget.itemWidget(item)
            actionTite = comboBox.currentText()
            listActions.append(actionTite)

        listActions = list(filter(lambda actionTitle: actionTitle != '', listActions))
        condDict = {'condTitle': condAndWidgetWithActions['condTitle'], 'actionsAssignedToCond': listActions}

        return condDict
