import gettext

from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QTextEdit, QAction
from PyQt5.QtGui import QKeySequence


_ = gettext.gettext


class TextEditWithClearing(QTextEdit):
    def __init__(self, parent=None):
        super(QTextEdit, self).__init__(parent)


    def contextMenuEvent(self, event) -> None:
        menu = self.createStandardContextMenu()

        clearAction = QAction(_("Clear"), self)
        clearAction.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_R))
        clearAction.triggered.connect(self.clear)

        menu.addSeparator()
        menu.addAction(clearAction)
        menu.exec(event.globalPos())
