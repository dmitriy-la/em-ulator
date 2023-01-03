from PyQt5.Qt import Qt, QApplication, QEvent, QRect, QPoint
from PyQt5.QtWidgets import QStyledItemDelegate, QItemDelegate, QStyleOptionButton, QStyle


class DelegateCheckBox(QStyledItemDelegate):
    """
    A delegate that places a fully functioning QCheckBox in every
    cell of the column to which it's applied
    """
    def __init__(self, parent):
        QItemDelegate.__init__(self, parent)


    def createEditor(self, parent, option, index) -> None:
        """
        Important, otherwise an editor is created if the user clicks in this cell.
        ** Need to hook up a signal to the model
        """

        return None


    def paint(self, painter, option, index) -> None:
        """
        Paint a checkbox without the label.
        """

        if index.data is str:
            if index.data() == "True":
                checked = True
            else:
                checked = False
        else:
            if index.data():
                checked = True
            else:
                checked = False

        check_box_style_option = QStyleOptionButton()

        if int(index.flags() & Qt.ItemIsEditable) > 0:
            check_box_style_option.state |= QStyle.State_Enabled
        else:
            check_box_style_option.state |= QStyle.State_ReadOnly

        if checked:
            check_box_style_option.state |= QStyle.State_On
        else:
            check_box_style_option.state |= QStyle.State_Off

        check_box_style_option.rect = self.getCheckBoxRect(option)

        check_box_style_option.state |= QStyle.State_Enabled

        QApplication.style().drawControl(QStyle.CE_CheckBox, check_box_style_option, painter)


    def editorEvent(self, event, model, option, index) -> bool:
        """
        Change the data in the model and the state of the checkbox
        if user presses the left mousebutton or presses
        Key_Space or Key_Select and this cell is editable. Otherwise do nothing.
        """
        if not int(index.flags() & Qt.ItemIsEditable) > 0:
            return False

        # Do not change the checkbox-state
        if event.type() == QEvent.MouseButtonPress:
            return False
        if event.type() == QEvent.MouseButtonRelease or event.type() == QEvent.MouseButtonDblClick:
            if event.button() != Qt.LeftButton or not self.getCheckBoxRect(option).contains(event.pos()):
                return False
            if event.type() == QEvent.MouseButtonDblClick:
                return True
        elif event.type() == QEvent.KeyPress:
            if event.key() != Qt.Key_Space and event.key() != Qt.Key_Select:
                return False
        else:
            return False

        self.setModelData(None, model, index)
        return True


    def setModelData(self, editor, model, index) -> None:
        """
        User wanted to change the state to the opposite.
        """

        if index.data is str:
            if index.data() == "True":
                newValue = False
            else:
                newValue = True
        else:
            if index.data():
                newValue = False
            else:
                newValue = True

        model.setData(index, newValue, Qt.EditRole)


    def getCheckBoxRect(self, option) -> QRect:
        check_box_style_option = QStyleOptionButton()
        check_box_rect = QApplication.style().subElementRect(QStyle.SE_CheckBoxIndicator, check_box_style_option, None)

        x = option.rect.x() + option.rect.width() / 2 - check_box_rect.width() / 2
        y = option.rect.y() + option.rect.height() / 2 - check_box_rect.height() / 2
        check_box_point = QPoint(x, y)

        return QRect(check_box_point, check_box_rect.size())
