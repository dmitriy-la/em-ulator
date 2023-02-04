import pytest
import sys

from PyQt5.QtCore import Qt, QModelIndex, QPoint
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

import src.windows.windowProfileEditor


@pytest.mark.parametrize("field_title, field_length, field_role, field_values_list",
                       [("MSG_LENGTH",     16,      "roleLength", []),
                        ("MSG_TYPE",        8,      "roleType",   ["01 - Test_msg_1"]),
                        ("MSG_ID",         16,      "roleId",     []),
                        ("4_BITS_FIELD",    4,      "roleOther",  ["1 - 1", "2 - 2", "3 - 3", "4 - 4"]),
                        ("12_BITS_FIELD",   12,     "roleOther",  []),
                        ("UNDEF_FIELD",  "undef.",  "roleOther",  []),
                        ("CRC",             32,     "roleCrc",    [])  ])
def enter_field_data(winProfileEditor, field_title, field_length, field_role, field_values_list):
    QTest.keyClicks(winProfileEditor.msgTypeEditor.fieldEditor.lineEditFieldTitle, field_title)
    QTest.keyClicks(winProfileEditor.msgTypeEditor.fieldEditor.lineEditFieldLength, field_length)

    winProfileEditor.msgTypeEditor.buttonSave()