import gettext
import socket

from PyQt5.Qt import Qt
from PyQt5.QtCore import QSize, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QCheckBox, QComboBox, QGroupBox
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit
from PyQt5.QtWidgets import QPushButton, QSpinBox, QVBoxLayout

import src.managers.managerDatalineSettings as managerDatalineSettings
import src.ui.windows.windowProfiledWindow as windowProfiledWindow


_ = gettext.gettext


class WindowDatalineSettings(windowProfiledWindow.WindowProfiledWindow):
    signalDatalineSettingsUpdated = pyqtSignal(dict)

    def __init__(self, profileTitle: str, parent=None):
        super().__init__(profileTitle, parent)
        self.datalineSettings = parent.datalineSettings
        self.profileTitle = profileTitle

        self.initUI()


    def initUI(self):
        self.setWindowProperties()

        self.principalLayout = QVBoxLayout(self)

        self.addGroupBoxNetSettings(self.principalLayout)
        self.comboBoxSendMode = self.addGroupBoxSendModeForTcpServer(self.principalLayout)

        self.addGroupBoxReceiptingSettings(self.principalLayout)
        self.addGroupBoxAutofillOptions(self.principalLayout)

        self.buttonSave.hide()
        self.buttonClose.hide()

        self.fillCurrentSettings()

        self.show()


    def setWindowProperties(self):
        self.setWindowTitle(_('Dataline settings - ') + str(self.parent.title))
        self.setModal(True)
        self.setFocusPolicy(Qt.StrongFocus)


    def addGroupBoxNetSettings(self, principalLayout: QVBoxLayout):
        groupBoxNetSettings = QGroupBox(self)
        vLayoutFullNetSettings = QVBoxLayout(self)

        settingsLayout = self.addSettingsLayout()

        vLayoutFullNetSettings.addLayout(settingsLayout)
        groupBoxNetSettings.setLayout(vLayoutFullNetSettings)
        groupBoxNetSettings.setTitle(_("Network settings"))

        self.addButtonRestartLayout(vLayoutFullNetSettings)

        principalLayout.addWidget(groupBoxNetSettings)


    def addButtonRestartLayout(self, vLayoutFullNetSettings):
        buttonRestartLayout = QHBoxLayout(self)
        buttonRestartLayout.addStretch(1)

        buttonRestart = self.getButtonRestart()
        buttonRestartLayout.addWidget(buttonRestart)

        buttonRestartLayout.addStretch(1)

        vLayoutFullNetSettings.addLayout(buttonRestartLayout)


    def getButtonRestart(self):
        buttonRestart = QPushButton(self)
        buttonRestart.setText(_('Restart with new settings'))
        buttonRestart.clicked.connect(self.restartNetworkThreadWithNewSettings)

        pixmap = QPixmap('../icons/play.png')
        playIcon = QIcon(pixmap)
        buttonRestart.setIcon(playIcon)
        buttonRestart.setIconSize(QSize(15, 15))

        return buttonRestart


    def addSettingsLayout(self) -> QHBoxLayout:
        settingsLayout = QHBoxLayout(self)

        self.addProtLayout(settingsLayout)
        self.addIpOwnLayout(settingsLayout)
        self.addPortOwnLayout(settingsLayout)
        self.addIpSendLayout(settingsLayout)
        self.addPortSendLayout(settingsLayout)

        return settingsLayout


    def addProtLayout(self, settingsLayout: QHBoxLayout):
        protLayout = QVBoxLayout(self)

        self.addLabelProtocol(protLayout)
        self.comboBoxProtocolType = self.addComboBoxProtocolType(protLayout)

        settingsLayout.addLayout(protLayout)


    def addLabelProtocol(self, protLayout: QVBoxLayout):
        labelProtocol = QLabel(_('Protocol'))
        protLayout.addWidget(labelProtocol)


    def addComboBoxProtocolType(self, protLayout: QVBoxLayout) -> QComboBox:
        comboBoxProtocolType = QComboBox(self)

        protList = ['TCP-server', 'TCP-client', 'UDP']
        comboBoxProtocolType.addItems(protList)

        comboBoxProtocolType.setCurrentText(self.datalineSettings["protocolType"])
        comboBoxProtocolType.setMinimumWidth(80)

        protLayout.addWidget(comboBoxProtocolType)

        return comboBoxProtocolType


    def addIpOwnLayout(self, settingsLayout: QHBoxLayout):
        ipOwnLayout = QVBoxLayout(self)

        self.addLabelIpOwn(ipOwnLayout)
        self.lineEditIpOwn = self.addLineEditIpOwn(ipOwnLayout)

        settingsLayout.addLayout(ipOwnLayout)


    def addLabelIpOwn(self, ipOwnLayout):
        labelIpOwn = QLabel(_('IP own.'))
        ipOwnLayout.addWidget(labelIpOwn)


    def addLineEditIpOwn(self, ipOwnLayout):
        lineEditIpOwn = QLineEdit(self)

        lineEditIpOwn.setMinimumWidth(70)
        lineEditIpOwn.setMaximumWidth(250)
        lineEditIpOwn.setText(self.datalineSettings["ipOwn"])

        ipOwnLayout.addWidget(lineEditIpOwn)

        return lineEditIpOwn


    def addPortOwnLayout(self, settingsLayout: QHBoxLayout):
        portOwnLayout = QVBoxLayout(self)

        labelPortIn = QLabel(_('Receipt port'))

        portOwnLayout.addWidget(labelPortIn)
        self.addSpinBoxPortOwn(portOwnLayout)

        settingsLayout.addLayout(portOwnLayout)


    def addSpinBoxPortOwn(self, portInLayout):
        self.spinBoxPortIn = QSpinBox(self)

        self.spinBoxPortIn.setMaximum(70000)
        self.spinBoxPortIn.setValue(self.datalineSettings["portOwn"])
        self.spinBoxPortIn.setMaximumWidth(150)

        portInLayout.addWidget(self.spinBoxPortIn)


    def addPortSendLayout(self, settingsLayout: QHBoxLayout):
        portOutLayout = QVBoxLayout(self)

        labelPortOut = QLabel(_('Send port'))

        portOutLayout.addWidget(labelPortOut)

        self.addSpinBoxPortSend(portOutLayout)

        settingsLayout.addLayout(portOutLayout)


    def addSpinBoxPortSend(self, portOutLayout):
        self.spinBoxPortOut = QSpinBox(self)

        self.spinBoxPortOut.setMaximum(70000)
        self.spinBoxPortOut.setMaximumWidth(150)
        self.spinBoxPortOut.setValue(self.datalineSettings["portSend"])

        portOutLayout.addWidget(self.spinBoxPortOut)


    def currentProtocolIsTcpServer(self) -> bool:
        if self.datalineSettings["protocolType"] == "TCP-server":
            return True
        else:
            return False


    def addGroupBoxSendModeForTcpServer(self, principalLayout: QVBoxLayout) -> QComboBox:
        groupBoxSendMode = QGroupBox(self)
        groupBoxSendMode.setTitle(_("Send mode if multiple clients connected"))

        if not self.currentProtocolIsTcpServer():
            groupBoxSendMode.hide()

        hLayoutSendMode = QHBoxLayout(self)
        comboBoxSendMode = QComboBox(self)
        choices = [_('send to all clients'), _('send to one client, switch between clients on tout')]
        comboBoxSendMode.addItems(choices)

        hLayoutSendMode.addWidget(comboBoxSendMode)

        groupBoxSendMode.setLayout(hLayoutSendMode)

        principalLayout.addWidget(groupBoxSendMode)

        return comboBoxSendMode


    def addGroupBoxReceiptingSettings(self, principalLayout):
        groupBoxReceiptingSettings = QGroupBox(self)
        vLayoutReceiptingSettings = QVBoxLayout(self)

        protLayout = QHBoxLayout(self)
        self.checkBoxAutoReceipt = self.addCheckBoxAutoReceipt(protLayout)
        self.spinBoxReceiptDelay = self.addSpinBoxReceiptDelay(protLayout)
        protLayout.addStretch(1)
        vLayoutReceiptingSettings.addLayout(protLayout)

        toutLayout = self.addToutLayout()
        vLayoutReceiptingSettings.addLayout(toutLayout)

        self.repsLayout = self.addRepsLayout()
        vLayoutReceiptingSettings.addLayout(self.repsLayout)

        vLayoutReceiptingSettings.addStretch()

        groupBoxReceiptingSettings.setLayout(vLayoutReceiptingSettings)
        groupBoxReceiptingSettings.setTitle(_("Receipting"))

        principalLayout.addWidget(groupBoxReceiptingSettings)


    def addSpinBoxReceiptDelay(self, protLayout):
        spinBoxReceiptDelay = QSpinBox(self)

        spinBoxReceiptDelay.setMaximum(30 * 60 * 1000)
        spinBoxReceiptDelay.setValue(self.datalineSettings["delay"])
        spinBoxReceiptDelay.setMaximumWidth(220)

        protLayout.addWidget(spinBoxReceiptDelay)

        return spinBoxReceiptDelay


    def addCheckBoxAutoReceipt(self, protLayout):
        checkBoxAutoReceipt = QCheckBox(self)

        checkBoxAutoReceipt.setText(_('Receipting on with delay, ms:'))
        checkBoxAutoReceipt.clicked.connect(self.setAutoReceipt)

        protLayout.addWidget(checkBoxAutoReceipt)

        return checkBoxAutoReceipt


    def addToutLayout(self):
        toutLayout = QHBoxLayout(self)

        labelTout = QLabel(_('Timeout awaiting receipt, ms'))
        toutLayout.addWidget(labelTout)

        self.spinBoxTout = self.addSpinBoxTout(toutLayout)
        toutLayout.addStretch(1)

        return toutLayout


    def addSpinBoxTout(self, toutLayout):
        spinBoxTout = QSpinBox(self)

        spinBoxTout.setMaximum(30 * 60 * 10000)
        spinBoxTout.setValue(self.datalineSettings["toutMs"])
        spinBoxTout.setMaximumWidth(220)

        spinBoxTout.valueChanged.connect(self.setReceiptTimeout)

        toutLayout.addWidget(spinBoxTout)

        return spinBoxTout


    def addRepsLayout(self):
        repsLayout = QHBoxLayout(self)

        labelRepeats = QLabel(_('Send attempts in case of receipt absence'))
        repsLayout.addWidget(labelRepeats)

        self.spinBoxRepeats = self.addSpinBoxRepeats(repsLayout)
        repsLayout.addStretch(1)

        return repsLayout


    def addSpinBoxRepeats(self, repsLayout):
        spinBoxRepeats = QSpinBox(self)

        spinBoxRepeats.setValue(self.datalineSettings["repeats"])
        spinBoxRepeats.setMaximumWidth(120)
        spinBoxRepeats.valueChanged.connect(self.setResendRepeats)

        repsLayout.addWidget(spinBoxRepeats)

        return spinBoxRepeats


    def addGroupBoxAutofillOptions(self, principalLayout):
        groupBoxAutofillOptions = QGroupBox(self)
        vLayoutAutofillOptions = QVBoxLayout(self)

        self.checkBoxTurnOffAutofillIdFields = self.addCheckBoxTurnOffAutofillIdFields(vLayoutAutofillOptions)
        self.checkBoxTurnOffAutofillCrcFields = self.addCheckBoxTurnOffAutofillCrcFields(vLayoutAutofillOptions)

        vLayoutAutofillOptions.addStretch(1)

        groupBoxAutofillOptions.setLayout(vLayoutAutofillOptions)
        groupBoxAutofillOptions.setTitle(_('Autofilling'))

        principalLayout.addWidget(groupBoxAutofillOptions)


    def addCheckBoxTurnOffAutofillIdFields(self, vLayoutAutofillOptions):
        checkBoxTurnOffAutofillIdFields = QCheckBox(self)

        checkBoxTurnOffAutofillIdFields.setText(_('Turn off autofilling for fields with role id'))
        checkBoxTurnOffAutofillIdFields.setChecked(False)
        checkBoxTurnOffAutofillIdFields.clicked.connect(self.setTurnOffAutofillIdFields)

        vLayoutAutofillOptions.addWidget(checkBoxTurnOffAutofillIdFields)

        return checkBoxTurnOffAutofillIdFields


    def addCheckBoxTurnOffAutofillCrcFields(self, vLayoutAutofillOptions):
        checkBoxTurnOffAutofillCrcFields = QCheckBox(self)

        checkBoxTurnOffAutofillCrcFields.setText(_('Turn off autofilling for field with role crc'))
        checkBoxTurnOffAutofillCrcFields.setChecked(False)
        checkBoxTurnOffAutofillCrcFields.clicked.connect(self.setTurnOffAutofillCrcFields)

        vLayoutAutofillOptions.addWidget(checkBoxTurnOffAutofillCrcFields)

        return checkBoxTurnOffAutofillCrcFields


    def addIpSendLayout(self, settingsLayout):
        ipSendLayout = QVBoxLayout(self)

        labelIpSend = QLabel(_('IP send'))
        ipSendLayout.addWidget(labelIpSend)

        self.addLineEditIpSend(ipSendLayout)

        settingsLayout.addLayout(ipSendLayout)


    def addLineEditIpSend(self, ipSendLayout):
        self.lineEditIpSend = QLineEdit(self)

        self.lineEditIpSend.setMinimumWidth(70)
        self.lineEditIpSend.setMaximumWidth(250)
        self.lineEditIpSend.setText(self.datalineSettings["ipSend"])

        ipSendLayout.addWidget(self.lineEditIpSend)


    def fillCurrentSettings(self):
        self.comboBoxProtocolType.setCurrentText(self.datalineSettings["protocolType"])
        self.lineEditIpOwn.setText(self.datalineSettings["ipOwn"])
        self.spinBoxPortIn.setValue(self.datalineSettings["portOwn"])
        self.lineEditIpSend.setText(self.datalineSettings["ipSend"])
        self.spinBoxPortOut.setValue(self.datalineSettings["portSend"])

        self.comboBoxSendMode.setCurrentText(self.datalineSettings["sendMode"])

        self.checkBoxAutoReceipt.setChecked(self.parent.receiptOn)
        self.spinBoxTout.setValue(self.datalineSettings["toutMs"])
        self.spinBoxRepeats.setValue(self.datalineSettings["repeats"])
        self.spinBoxReceiptDelay.setValue(self.datalineSettings["delay"])

        self.checkBoxTurnOffAutofillIdFields.setChecked(not self.parent.autofillId)
        self.checkBoxTurnOffAutofillCrcFields.setChecked(not self.parent.autofillCrc)


    @pyqtSlot()
    def setAutoReceipt(self):
        self.parent.receiptOn = self.checkBoxAutoReceipt.isChecked()


    @pyqtSlot()
    def setReceiptTimeout(self):
        self.parent.receiptToutMs = self.spinBoxTout.value()


    @pyqtSlot()
    def setResendRepeats(self):
        self.parent.resendRepeats = self.spinBoxRepeats.value()


    @pyqtSlot()
    def setTurnOffAutofillIdFields(self):
        self.parent.autofillId = not self.checkBoxTurnOffAutofillIdFields.isChecked()


    @pyqtSlot()
    def setTurnOffAutofillCrcFields(self):
        self.parent.autofillCrc = not self.checkBoxTurnOffAutofillCrcFields.isChecked()


    def isValidIpAddressV4(self, address) -> bool:
        try:
            socket.inet_pton(socket.AF_INET, address)
        except AttributeError:  # no inet_pton
            try:
                socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error:  # not valid
            return False

        return True


    def isValidIpAddressV6(self, address) -> bool:
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:  # not a valid address
            return False
        return True


    def isValidIp(self, address) -> bool:
        if self.isValidIpAddressV4(address) or self.isValidIpAddressV4(address):
            return True
        else:
            return False


    def closeEvent(self, event):
        self.parent.datalineSettingsWindowIsShown = False

        datalineManager = managerDatalineSettings.ManagerDatalineSettings(self.profileTitle)
        self.datalineSettings = self.getCurrentDatalineSettings()

        datalineManager.updateDatalineSettingsOfSingleDataline(self.datalineSettings)

        self.parent.updateDatalineSettings()


    def getCurrentDatalineSettings(self):
        self.datalineSettings["protocolType"] = self.comboBoxProtocolType.currentText()
        self.datalineSettings["ipOwn"] = self.lineEditIpOwn.text()
        self.datalineSettings["portOwn"] = self.spinBoxPortIn.value()
        self.datalineSettings["ipSend"] = self.lineEditIpSend.text()
        self.datalineSettings["portSend"] = self.spinBoxPortOut.value()

        self.datalineSettings["sendMode"] = self.comboBoxSendMode.currentText()

        self.datalineSettings["toutMs"] = self.spinBoxTout.value()
        self.datalineSettings["repeats"] = self.spinBoxRepeats.value()
        self.datalineSettings["delay"] = self.spinBoxReceiptDelay.value()

        return self.datalineSettings


    def restartNetworkThreadWithNewSettings(self):
        enteredIp = self.lineEditIpOwn.text()

        if self.isValidIp(enteredIp):
            self.setStateLabelToStop()

            self.parent.networkThread.closeSockets()
            self.parent.networkThread.terminate()

            self.datalineSettings = self.getCurrentDatalineSettings()

            self.parent.startNetworkThread()
        else:
            self.parent.showErrorMessageBox(_('IP-address entered is wrong'), _('Check'))


    def setStateLabelToStop(self):
        self.parent.labelNetStateCurrent.setText(_('STOP'))
        self.parent.labelNetStateCurrent.setStyleSheet('QLabel {background-color : red; }')


    def stopNetworkThread(self):
        self.parent.msgToBeSent.clear()
        self.setStateLabelToStop()

        self.parent.networkThread.closeSockets()
        self.parent.networkThread.terminate()
