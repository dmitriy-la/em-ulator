from PyQt5.Qt import Qt, QObject, pyqtSignal, QModelIndex, QApplication, pyqtSlot
from PyQt5.QtWidgets import QItemDelegate, QComboBox, QStyleOptionComboBox, QStyle


class Communicate(QObject):
    dataChanged = pyqtSignal(QModelIndex, QModelIndex)


class DelegateComboBox(QItemDelegate):
    def __init__(self, owner, choices):
        super().__init__(owner)
        self.items = choices
        self.communicate = Communicate()


    def createEditor(self, parent, option, index) -> QComboBox:
        self.editor = QComboBox(parent)

        self.editor.addItems(self.items)

        self.editor.currentTextChanged.connect(self.currentTextChanged)

        return self.editor


    def paint(self, painter, option, index) -> None:
        value = index.data(Qt.DisplayRole)
        style = QApplication.style()
        opt = QStyleOptionComboBox()
        opt.text = str(value)
        opt.rect = option.rect

        style.drawComplexControl(QStyle.CC_ComboBox, opt, painter)

        QItemDelegate.paint(self, painter, option, index)


    def setEditorData(self, editor, index) -> None:
        value = index.data(Qt.DisplayRole)
        num = self.items.index(value)
        editor.setCurrentIndex(num)


    def setModelData(self, editor, model, index) -> None:
        value = editor.currentText()

        self.communicate.dataChanged.emit(index, index)
        model.setData(index, value, Qt.EditRole)


    def updateEditorGeometry(self, editor, option, index) -> None:
        editor.setGeometry(option.rect)


    @pyqtSlot()
    def currentTextChanged(self) -> None:
        self.commitData.emit(self.sender())