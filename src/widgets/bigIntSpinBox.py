from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QAbstractSpinBox, QLineEdit
from PyQt5.QtCore import QRegExp, pyqtSlot


class BigIntSpinBox(QAbstractSpinBox):
    def __init__(self, parent=None):
        super(BigIntSpinBox, self).__init__(parent)

        self.step = 1
        self.min = 0
        self.max = 1

        self.lineEdit = QLineEdit(self)

        regexp = QRegExp("[0-9A-Fa-f]{1}")
        validator = QRegExpValidator(regexp, self)
        self.lineEdit.setValidator(validator)
        self.lineEdit.textEdited.connect(self.onLineEditTextEdit)

        self.setLineEdit(self.lineEdit)


    def value(self) -> int:
        try:
            if self.lineEdit.text() != '':
                return int(self.lineEdit.text(), 16)
        except ValueError:
            raise


    @pyqtSlot(str)
    def onLineEditTextEdit(self, text: str) -> None:
        try:
            valueInt = int(text, 16)
            self.setValue(valueInt)
        except ValueError:
            print('ValueError somehow!')


    def setValue(self, value) -> None:
        if self.valueInRange(value):
            valueStr = '{:0X}'.format(value)
            self.lineEdit.setText(valueStr)
        elif value > self.maximum():
            value = self.maximum()
            valueStr = '{:0X}'.format(value)
            self.lineEdit.setText(valueStr)
        elif value < self.minimum():
            value = self.minimum()
            valueStr = '{:0X}'.format(value)
            self.lineEdit.setText(valueStr)


    def stepBy(self, steps) -> None:
        self.setValue(self.value() + steps * self.singleStep())


    def stepEnabled(self):
        return self.StepUpEnabled | self.StepDownEnabled


    def singleStep(self) -> int:
        return self.step


    def minimum(self) -> int:
        return self.min


    def setMinimum(self, minimum: int) -> None:
        assert isinstance(minimum, int)
        self.min = minimum


    def maximum(self) -> int:
        return self.max


    def setMaximum(self, maximum: int) -> None:
        assert isinstance(maximum, int)
        self.max = maximum


    def setBitLengthToDisplay(self, bitLength: int) -> None:
        maximum = pow(2, bitLength)
        maximum -= 1

        qregexp = self.getQRegexpFromBitLength(bitLength)
        validator = QRegExpValidator(qregexp, self)
        self.lineEdit.setValidator(validator)

        self.max = maximum

        if self.lineEdit.text() != '':
            intValue = int(self.lineEdit.text(), 16)
            if intValue > self.max:
                self.setValue(intValue)


    def getQRegexpFromBitLength(self, bitLength: int) -> QRegExp:
        numberOfSymbolsAllowedToEnterByUser = (bitLength // 4) + 1
        regexp = "[0-9A-Fa-f]{" + str(numberOfSymbolsAllowedToEnterByUser) + "}"

        regexp = QRegExp(regexp)

        return regexp


    def valueInRange(self, value: int) -> bool:
        if value in range(self.minimum(), self.maximum()):
            return True
        else:
            return False
