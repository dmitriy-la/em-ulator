import gettext
import shutil

from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSlot, QSize
from PyQt5.QtWidgets import QAbstractItemView, QTableView,  \
                            QFileDialog, QInputDialog,      \
                            QHBoxLayout, QVBoxLayout,       \
                            QGroupBox, QLabel, QLineEdit, QPushButton, QSpinBox, QSplitter, QHeaderView
from PyQt5.QtGui import QPixmap, QIcon

import managers.managerMsgFormats
import managers.managerDatalineSettings
import managers.managerProfiles
import datamodels.dataModelMsgTypes
import datamodels.dataModelDataline
import delegates.delegateComboBox
import delegates.delegateCheckBox
import windows.windowProfiledWindow
import windows.windowTypeOfMsgEditor
import windows.windowAutorespModesEditor


_ = gettext.gettext


class WindowProfileEditor(windows.windowProfiledWindow.WindowProfiledWindow):
    def __init__(self, profileTitle='default', parent=None):
        super().__init__(profileTitle, parent)
        self.typesOfMsgModel = datamodels.dataModelMsgTypes.DataModelMsgTypes()

        self.datalineModel = datamodels.dataModelDataline.DataModelDataline()

        self.windowAutorespEditorList = []

        self.formatManager = managers.managerMsgFormats.ManagerMsgFormats(self.profileTitle)

        self.initUI()

        self.readProfileInfoIntoForm()


    def readProfileInfoIntoForm(self) -> None:
        self.refreshDatalineList()
        self.refreshMsgTypeList()


    def initUI(self) -> None:
        self.setWindowProperties()

        self.principalLayout = QHBoxLayout(self)

        self.principalSplitter = QSplitter(self)
        self.principalSplitter.setOrientation(Qt.Horizontal)

        self.principalLayout.addWidget(self.principalSplitter)

        self.principalVertLayout = self.getPrincipalVertLayout()
        self.principalLayout.addLayout(self.principalVertLayout)

        self.datalineEditorGroupBox = self.getDatalineEditorGroupBox()
        self.msgEditGroupBox = self.getMsgEditorGroupBox()

        self.principalSplitter.addWidget(self.datalineEditorGroupBox)
        self.principalSplitter.addWidget(self.msgEditGroupBox)

        self.addCheckBoxToColumn(1)
        self.addCheckBoxToColumn(2)

        self.show()


    def setWindowProperties(self) -> None:
        self.title = _('Profile Configuration - ')
        self.title += self.profileTitle
        self.setWindowTitle(self.title)

        self.xCoord = 300
        self.yCoord = 150
        self.height = 500
        self.width = 800
        self.setGeometry(self.xCoord, self.yCoord, self.width, self.height)

        flags = self.windowFlags()
        self.setWindowFlags(int(flags) | Qt.Tool)

        self.setModal(True)
        self.setFocusPolicy(Qt.StrongFocus)


    def getPrincipalVertLayout(self) -> QVBoxLayout:
        """

        :return:
        """
        principalVertLayout = QVBoxLayout(self)

        self.layoutEnterProfileTitle = self.getHLayEnterProfileTitle()
        principalVertLayout.addLayout(self.layoutEnterProfileTitle)

        self.hLayOtherSettings = self.getHLayOtherSettings()
        principalVertLayout.addWidget(self.principalSplitter)
        principalVertLayout.addLayout(self.hLayOtherSettings)

        hButtonLayout = self.getHLayButtonsSaveCancel()
        principalVertLayout.addLayout(hButtonLayout)

        return principalVertLayout


    def getHLayEnterProfileTitle(self) -> QHBoxLayout:
        """

        :return:
        """
        layoutEnterProfileTitle = QHBoxLayout(self)

        lableEnterProfileTitle = QLabel(self)
        lableEnterProfileTitle.setText(_('Enter profile title:'))
        lableEnterProfileTitle.hide()

        self.lineEditProfileTitle = QLineEdit(self)
        self.lineEditProfileTitle.setText(self.profileTitle)
        self.lineEditProfileTitle.hide()

        layoutEnterProfileTitle.addWidget(lableEnterProfileTitle)
        layoutEnterProfileTitle.addWidget(self.lineEditProfileTitle)

        return layoutEnterProfileTitle


    def getHLayOtherSettings(self) -> QHBoxLayout:
        """

        :return:
        """
        hLayOtherSettings = QHBoxLayout(self)

        self.addButtonMaxLengthAndOtherPacketsSettings(hLayOtherSettings)
        self.addButtonAutorespSettings(hLayOtherSettings)

        self.buttonEnterHexMaskForReceipt = self.getButtonEnterHexMaskForGettingReceiptTypeFromMsgType(hLayOtherSettings)

        # Not tested yet
        return hLayOtherSettings


    def getButtonEnterHexMaskForGettingReceiptTypeFromMsgType(self, hLayOtherSettings) -> None:
        self.buttonEnterHexMaskForReceipt = QPushButton(self)
        self.buttonEnterHexMaskForReceipt.setText(_("Set up mask for creating receipt\'s type"))
        self.buttonEnterHexMaskForReceipt.clicked.connect(self.showDialogEnterMaskForReceiptType)

        self.buttonEnterHexMaskForReceipt.setEnabled(False)

        hLayOtherSettings.addWidget(self.buttonEnterHexMaskForReceipt)


    def addButtonMaxLengthAndOtherPacketsSettings(self, hLayOtherSettings) -> None:
        buttonSetMaxLenAndPackingSettings = QPushButton(self)
        buttonSetMaxLenAndPackingSettings.setText(_("Max length and other packets settings"))
        buttonSetMaxLenAndPackingSettings.clicked.connect(self.setMaxLenAndPackingSettings)

        # Not functional yet
        buttonSetMaxLenAndPackingSettings.setEnabled(False)

        hLayOtherSettings.addWidget(buttonSetMaxLenAndPackingSettings)


    def addButtonAutorespSettings(self, hLayOtherSettings) -> None:
        buttonAutorespSettings = QPushButton(self)
        buttonAutorespSettings.setText(_("Autoresponse settings"))
        buttonAutorespSettings.clicked.connect(self.setAutorespSettings)

        pixmap = QPixmap('../icons/settings.png')
        saveIcon = QIcon(pixmap)
        buttonAutorespSettings.setIcon(saveIcon)
        buttonAutorespSettings.setIconSize(QSize(15, 15))

        hLayOtherSettings.addWidget(buttonAutorespSettings)


    def showDialogEnterMaskForReceiptType(self) -> None:
        """

        :return:
        """
        maskForReceiptTypeDialog = self.getMaskForReceiptTypeDialog()

        result = maskForReceiptTypeDialog.exec()
        if result:
            spinBoxWithMask = maskForReceiptTypeDialog.findChild(QSpinBox)
            mask = spinBoxWithMask.text()
            text = _('Hex mask for forming receipt type')
            text += mask

            self.buttonEnterHexMaskForReceipt.setText(text)

            profileManager = managers.managerProfiles.ManagerProfiles(self.profileTitle)
            profileManager.setMaskForFormingReceiptType(mask)


    def getMaskForReceiptTypeDialog(self):
        maskForReceiptTypeDialog = QInputDialog(self)
        maskForReceiptTypeDialog.setWindowTitle(_("Enter mask"))
        maskForReceiptTypeDialog.setLabelText(_("Some protocols have variable receipt type,") + '\n' +
                                              _("which is formed by applying mask over message type in received msg"))
        maskForReceiptTypeDialog.setIntRange(0, 2147483647)
        maskForReceiptTypeDialog.setIntValue(0)
        maskForReceiptTypeDialog.setIntStep(1)
        maskForReceiptTypeDialog.doubleMaximum()

        spinBox = maskForReceiptTypeDialog.findChild(QSpinBox)
        spinBox.setDisplayIntegerBase(16)
        spinBox.setRange(0, 2147483647)

        return maskForReceiptTypeDialog


    def getHLayButtonsSaveCancel(self) -> QHBoxLayout:
        """

        :return:
        """
        self.buttonSave.clicked.connect(self.onClickSaveProfile)
        self.buttonClose.clicked.connect(self.onClickClose)
        #
        hButtonLayout = QHBoxLayout()
        hButtonLayout.addStretch(1)
        hButtonLayout.setSpacing(0)
        hButtonLayout.addWidget(self.buttonSave)
        hButtonLayout.addWidget(self.buttonClose)

        return hButtonLayout


    def getMsgEditorGroupBox(self) -> QGroupBox:
        """

        :return:
        """
        self.vLayoutMsgEditor = self.getVLayForMsgEditor()

        msgEditGroupBox = QGroupBox(self)
        msgEditGroupBox.setTitle(_('MSG Editor'))
        msgEditGroupBox.setLayout(self.vLayoutMsgEditor)

        return msgEditGroupBox


    def getDatalineEditorGroupBox(self) -> QGroupBox:
        """

        :return:
        """
        self.vLayoutDatalineEditor = self.getVLayForDatalineEditor()

        datalineEditorGroupBox = QGroupBox(self)
        datalineEditorGroupBox.setTitle(_('Dataline Editor'))
        datalineEditorGroupBox.setLayout(self.vLayoutDatalineEditor)

        return datalineEditorGroupBox


    def getVLayForMsgEditor(self) -> QVBoxLayout:
        """

        :return:
        """
        vLayoutMsgEditor = QVBoxLayout(self)

        buttonOpenFileMsgFormats = self.getButtonOpenFileMsgFormats()
        hLayoutUpper = self.getHLayUpperForMsgTypeManagement()

        self.tableViewMsgTypes = self.getTableViewMsgTypes()
        self.typesOfMsgModel = datamodels.dataModelMsgTypes.DataModelMsgTypes()
        self.tableViewMsgTypes.setModel(self.typesOfMsgModel)
        self.selectionModelMsgTypes = self.tableViewMsgTypes.selectionModel()

        vLayoutMsgEditor.addWidget(buttonOpenFileMsgFormats)

        vLayoutMsgEditor.addLayout(hLayoutUpper)
        vLayoutMsgEditor.addWidget(self.tableViewMsgTypes)

        return vLayoutMsgEditor


    def getTableViewMsgTypes(self) -> QTableView:
        """

        :return:
        """
        tableViewMsgTypes = QTableView(self)
        tableViewMsgTypes.setSelectionBehavior(QAbstractItemView.SelectRows)

        tableViewMsgTypes.horizontalHeader().setStretchLastSection(True)
        tableViewMsgTypes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        tableViewMsgTypes.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        tableViewMsgTypes.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        tableViewMsgTypes.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        return tableViewMsgTypes


    def getHLayUpperForMsgTypeManagement(self) -> QHBoxLayout:
        """

        :return:
        """
        hLayoutUpper = QHBoxLayout()
        hLayoutUpper.setSpacing(0)

        self.addLabelMsgTypes(hLayoutUpper)
        hLayoutUpper.addStretch(1)
        self.addButtonAddMsgType(hLayoutUpper)
        self.addButtonEditMsgType(hLayoutUpper)
        self.addButtonRemoveMsgType(hLayoutUpper)

        return hLayoutUpper


    def addLabelMsgTypes(self, hLayoutUpper):
        labelMsgTypes = QLabel(self)
        labelMsgTypes.setText(_('Message types:'))
        hLayoutUpper.addWidget(labelMsgTypes)


    def addButtonAddMsgType(self, hLayoutUpper):
        buttonAddMsgType = QPushButton(self)
        buttonAddMsgType.setText(_('Add MSG type'))
        buttonAddMsgType.clicked.connect(self.onClickAddMsgType)

        pixmap = QPixmap('../icons/add-document.png')
        saveIcon = QIcon(pixmap)
        buttonAddMsgType.setIcon(saveIcon)
        buttonAddMsgType.setIconSize(QSize(15, 15))

        hLayoutUpper.addWidget(buttonAddMsgType)


    def addButtonEditMsgType(self, hLayoutUpper):
        buttonEditMsgType = QPushButton(self)
        buttonEditMsgType.setText(_('Edit MSG type'))
        buttonEditMsgType.clicked.connect(self.onClickEditMsgType)

        pixmap = QPixmap('../icons/edit.png')
        saveIcon = QIcon(pixmap)
        buttonEditMsgType.setIcon(saveIcon)
        buttonEditMsgType.setIconSize(QSize(15, 15))

        hLayoutUpper.addWidget(buttonEditMsgType)


    def addButtonRemoveMsgType(self, hLayoutUpper) -> None:
        buttonRemoveMsgType = QPushButton(self)
        buttonRemoveMsgType.setText(_('Remove MSG type'))

        buttonRemoveMsgType.clicked.connect(self.onClickRemoveMsgType)

        pixmap = QPixmap('../icons/trash.png')
        saveIcon = QIcon(pixmap)
        buttonRemoveMsgType.setIcon(saveIcon)
        buttonRemoveMsgType.setIconSize(QSize(15, 15))

        hLayoutUpper.addWidget(buttonRemoveMsgType)


    def getButtonOpenFileMsgFormats(self) -> QPushButton:
        """

        :return:
        """
        buttonOpenFileMsgFormats = QPushButton(self)
        buttonOpenFileMsgFormats.setText(_('Open MSG file formats'))
        buttonOpenFileMsgFormats.clicked.connect(self.onClickOpenFileWithMsgFormats)

        pixmap = QPixmap('../icons/folder.png')
        saveIcon = QIcon(pixmap)
        buttonOpenFileMsgFormats.setIcon(saveIcon)
        buttonOpenFileMsgFormats.setIconSize(QSize(15, 15))

        return buttonOpenFileMsgFormats


    def getVLayForDatalineEditor(self) -> QVBoxLayout:
        """

        :return:
        """
        self.tableViewDataline = self.getTableViewDataline()
        self.selectionModelDataline = self.tableViewDataline.selectionModel()
        self.addComboBoxToProtocolColumn()
        self.addComboBoxToSendModeColumn()

        hButtonLayout = self.getHLayAddRemoveDataline()

        vLayoutLeft = QVBoxLayout(self)
        vLayoutLeft.addLayout(hButtonLayout)
        vLayoutLeft.addSpacing(5)
        vLayoutLeft.addWidget(self.tableViewDataline)

        return vLayoutLeft


    def getTableViewDataline(self) -> QTableView:
        """

        :return:
        """
        tableViewDataline = QTableView(self)
        tableViewDataline.setModel(self.datalineModel)
        tableViewDataline.setToolTip(_('Enter dataline parameters'))
        tableViewDataline.setSelectionBehavior(QAbstractItemView.SelectRows)

        tableViewDataline.horizontalHeader().setStretchLastSection(True)
        tableViewDataline.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        tableViewDataline.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        tableViewDataline.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        tableViewDataline.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        return tableViewDataline


    def getHLayAddRemoveDataline(self) -> QHBoxLayout:
        """

        :return:
        """
        hButtonLayout = QHBoxLayout()

        self.addButtonAddDataline(hButtonLayout)
        self.addButtonRemoveDataline(hButtonLayout)

        hButtonLayout.addStretch(1)

        return hButtonLayout


    def addButtonAddDataline(self, hButtonLayout) -> None:
        buttonAddDataline = QPushButton(self)
        buttonAddDataline.setText(_('Add dataline'))
        buttonAddDataline.clicked.connect(self.onClickAddDataline)

        pixmap = QPixmap('../icons/add-document.png')
        saveIcon = QIcon(pixmap)
        buttonAddDataline.setIcon(saveIcon)
        buttonAddDataline.setIconSize(QSize(15, 15))

        hButtonLayout.addWidget(buttonAddDataline)


    def addButtonRemoveDataline(self, hButtonLayout) -> None:
        buttonRemoveDataline = QPushButton(self)
        buttonRemoveDataline.setText(_('Remove dataline'))
        buttonRemoveDataline.clicked.connect(self.onClickDelDataline)

        pixmap = QPixmap('../icons/trash.png')
        saveIcon = QIcon(pixmap)
        buttonRemoveDataline.setIcon(saveIcon)
        buttonRemoveDataline.setIconSize(QSize(15, 15))

        hButtonLayout.addWidget(buttonRemoveDataline)


    def setMaxLenAndPackingSettings(self) -> None:
        """

        :return:
        """
        pass


    def setAutorespSettings(self) -> None:
        """

        :return:
        """
        self.windowAutorespEditorList.clear()
        window = windows.windowAutorespModesEditor.WindowAutorespModesEditor(self.profileTitle)
        self.windowAutorespEditorList.append(window)


    def addComboBoxToProtocolColumn(self) -> None:
        """

        :return:
        """
        choices = ['TCP-server', 'TCP-client', 'UDP', 'raw']
        protocolsColumnNum = 1
        self.addComboBoxWithChoicesToColumn(choices, protocolsColumnNum)


    def addComboBoxToSendModeColumn(self) -> None:
        choices = [_('send to all clients'), _('send to one client, switch between clients on tout')]
        protocolsColumnNum = 9

        self.addComboBoxWithChoicesToColumn(choices, protocolsColumnNum)


    def addComboBoxWithChoicesToColumn(self, choices, columnNum) -> None:
        delegateComboBox = delegates.delegateComboBox.DelegateComboBox(self.datalineModel, choices)
        self.tableViewDataline.setItemDelegateForColumn(columnNum, delegateComboBox)

        # supposedly makes combo boxes editable with a single-click:
        for row in range(self.datalineModel.rows):
            self.tableViewDataline.openPersistentEditor(self.datalineModel.index(row, columnNum))


    def addCheckBoxToColumn(self, colNum: int) -> None:
        """

        :param colNum:
        :return:
        """
        checkBox = delegates.delegateCheckBox.DelegateCheckBox(self.tableViewMsgTypes)
        self.tableViewMsgTypes.setItemDelegateForColumn(colNum, checkBox)


    @pyqtSlot()
    def onClickAddDataline(self) -> None:
        """

        :return:
        """
        title = "default " + str(self.datalineModel.rows)
        datalineDict = {"title": title,
                        "protocolType": "TCP-server",
                        "ipOwn": "127.0.0.1",
                        "portOwn": 2048,
                        "ipSend": "127.0.0.1",
                        "portSend": 2048,
                        "toutMs": 20000,
                        "repeats": 2,
                        "delay": 1000,
                        "sendMode": "send to all clients"}
        self.datalineModel.appendDatalineRow(datalineDict)
        self.updateDatalineSettings()


    @pyqtSlot()
    def onClickDelDataline(self) -> None:
        """

        :return:
        """
        indexes = self.selectionModelDataline.selectedIndexes()

        # none selected - do nothing
        if len(indexes) <= 0:
            return

        firstRowToDel = indexes[0].row()
        lastRowToDel = indexes[len(indexes) - 1].row()
        rowsCountToDelete = lastRowToDel - firstRowToDel + 1
        self.datalineModel.removeRows(firstRowToDel, rowsCountToDelete)


    @pyqtSlot()
    def onClickOpenFileWithMsgFormats(self) -> None:
        """

        :return:
        """
        file = QFileDialog.getOpenFileName(None, _("Select existing file formats"), "", "json(*.json)")

        formatsFilePath = './__profiles__/' + self.profileTitle + '/msgFormats.json'

        try:
            shutil.copy(file[0], formatsFilePath)
        except FileNotFoundError:
            print("No pathfile")

        self.refreshMsgTypeList()


    @pyqtSlot()
    def onClickSaveProfile(self) -> None:
        """

        :return:
        """
        self.updateDatalineSettings()

        self.formatManager.updateAllFormatsFromAllMsgTypesList(self.typesOfMsgModel.msgTypesList)

        successText = _("Profile") + " \"" + self.profileTitle + "\" " + _("saved.")

        self.showSuccessMessageBox(successText)


    def updateDatalineSettings(self) -> None:
        """

        :return:
        """
        datalineManager = managers.managerDatalineSettings.ManagerDatalineSettings(self.profileTitle)
        datalineManager.updateDatalineSettingsFile(self.datalineModel.datalineList)


    @pyqtSlot()
    def refreshMsgTypeList(self) -> None:
        """

        :return:
        """
        self.formatManager.readMsgFormatsList()

        allMsgTypes = self.formatManager.getListOfAllMsgTypeTitles()

        self.typesOfMsgModel.msgTypesList.clear()
        self.typesOfMsgModel.removeRows(0, self.typesOfMsgModel.rows)

        for msgType in allMsgTypes:
            msgTypeInfo = self.formatManager.getInfoForMsgType(msgType)
            self.typesOfMsgModel.appendMsgType(msgTypeInfo)

        msgTypesCount = len(allMsgTypes)
        for row in range(msgTypesCount):
            self.tableViewMsgTypes.openPersistentEditor(self.typesOfMsgModel.index(row, 1))
            self.tableViewMsgTypes.openPersistentEditor(self.typesOfMsgModel.index(row, 2))


    @pyqtSlot()
    def refreshDatalineList(self) -> None:
        """

        :return:
        """
        datalineManager = managers.managerDatalineSettings.ManagerDatalineSettings(self.profileTitle)
        datalineList = datalineManager.getDatalineSettingsList()

        self.typesOfMsgModel.msgTypesList.clear()
        self.typesOfMsgModel.removeRows(0, self.typesOfMsgModel.rows)

        for dataline in datalineList:
            self.datalineModel.appendDatalineRow(dataline)

        self.updateDatalineSettings()


    @pyqtSlot()
    def onClickAddMsgType(self) -> None:
        """

        :return:
        """
        self.profileTitle = self.lineEditProfileTitle.text()
        self.msgTypeEditor = windows.windowTypeOfMsgEditor.WindowTypeOfMsgEditor(self.profileTitle)
        self.msgTypeEditor.signalMsgTypeEditorWindowClosed.connect(self.refreshMsgTypeList)


    @pyqtSlot()
    def onClickEditMsgType(self) -> None:
        """

        :return:
        """
        indexes = self.selectionModelMsgTypes.selectedIndexes()

        # none selected - do nothin
        if len(indexes) <= 0:
            print('nothing selected', indexes)
            return

        msgType = [cell.data() for cell in indexes if cell.column() == 0][0]

        self.msgTypeEditor = windows.windowTypeOfMsgEditor.WindowTypeOfMsgEditor(self.profileTitle, msgType)
        self.msgTypeEditor.signalMsgTypeEditorWindowClosed.connect(self.refreshMsgTypeList)


    @pyqtSlot()
    def onClickRemoveMsgType(self) -> None:
        """
        :return:
        """
        indexes = self.selectionModelMsgTypes.selectedIndexes()

        if len(indexes) <= 0:
            return

        msgType = [cell.data() for cell in indexes if cell.column() == 0][0]

        self.formatManager.removeMsgType(msgType)

        self.refreshMsgTypeList()


    @pyqtSlot()
    def onClickClose(self) -> None:
        """
        :return:
        """
        self.windowAutorespEditorList.clear()
        self.close()