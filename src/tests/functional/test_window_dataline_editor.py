import pytest
import sys

from PyQt5.QtCore import Qt, QModelIndex, QPoint
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

import src.ui.windows.windowProfileSelect
import src.ui.windows.windowProfileEditor

import src.managers.managerProfiles
import src.managers.managerDatalineSettings

TEST_PROFILE_STR = "test_profile"


def test_dataline_editor(mocker, mocker_dataline_settings_file_with_one_dataline):
    test_app = QApplication(sys.argv)

    mocker.patch('src.managers.managerProfiles.ManagerProfiles.getMaskForFormingReceiptType', return_value="")
    mocker.patch('src.managers.managerMsgFormats.ManagerMsgFormats.getListOfAllMsgTypeTitles', return_value=[])

    check_adding_dataline_to_dataline_editor(mocker_dataline_settings_file_with_one_dataline)
    check_removing_dataline_from_dataline_editor(mocker_dataline_settings_file_with_one_dataline)


def check_adding_dataline_to_dataline_editor(mocker_dataline_settings_file_with_one_dataline):
    win_profile_editor = src.ui.windows.windowProfileEditor.WindowProfileEditor(TEST_PROFILE_STR)

    select_row_in_dataline_table(win_profile_editor, 0)

    win_profile_editor.onClickAddDataline()

    assert len(win_profile_editor.datalineModel.datalineList) == 2


@pytest.fixture
def mocker_dataline_settings_file_with_one_dataline(mocker):
    mock_dataline_file = mocker.mock_open(read_data="""[{"title": "serv",
                                     "protocolType": "TCP-server",
                                     "ipOwn": "127.0.0.1",
                                     "portOwn": 2048,
                                     "ipSend": "127.0.0.1",
                                     "portSend": 2050,
                                     "toutMs": 3000,
                                     "repeats": 2,
                                     "delay": 100,
                                     "sendMode": "send to all clients"}]""")
    builtin_open = "builtins.open"
    mocker.patch(builtin_open, mock_dataline_file)

    return mock_dataline_file


def select_row_in_dataline_table(win_profile_editor, row: int):
    xPos = win_profile_editor.tableViewDataline.rowViewportPosition(row)
    yPos = win_profile_editor.tableViewDataline.columnViewportPosition(0) + 5
    pointInsideFirstCellOfFirstRow = QPoint(xPos, yPos)

    tableViewport = win_profile_editor.tableViewDataline.viewport()
    QTest.mouseClick(tableViewport, Qt.LeftButton, Qt.KeyboardModifier(), pointInsideFirstCellOfFirstRow)


def check_removing_dataline_from_dataline_editor(mocker_dataline_settings_file_with_one_dataline):
    win_profile_editor = src.ui.windows.windowProfileEditor.WindowProfileEditor(TEST_PROFILE_STR)

    select_row_in_dataline_table(win_profile_editor, 0)
    win_profile_editor.onClickRemoveDataline()

    assert len(win_profile_editor.datalineModel.datalineList) == 0


INDEX_OF_COLUMN_WITH_IP_OWN = 2
INDEX_OF_COLUMN_WITH_IP_SEND = 4
@pytest.mark.parametrize("ip_user_input, expected_set_result", [("not_numeric", False),
                                                                ("6666.7777.888.999", False),
                                                                ("127.0.0.12.1", False),
                                                                ("256.256.256.256", False),
                                                                ("256.168.12.1", False),
                                                                ("255.168.12.1", True),
                                                                ("192.168.12.1", True)])
@pytest.mark.parametrize("column_to_check", (INDEX_OF_COLUMN_WITH_IP_OWN, INDEX_OF_COLUMN_WITH_IP_SEND))
def test_editing_ip(mocker, mocker_dataline_settings_file_with_one_dataline, column_to_check, ip_user_input,
                    expected_set_result):
    test_app = QApplication(sys.argv)

    mocker.patch('src.managers.managerProfiles.ManagerProfiles.getMaskForFormingReceiptType', return_value="")
    mocker.patch('src.managers.managerMsgFormats.ManagerMsgFormats.getListOfAllMsgTypeTitles', return_value=[])

    win_profile_editor = src.ui.windows.windowProfileEditor.WindowProfileEditor(TEST_PROFILE_STR)

    model = win_profile_editor.tableViewDataline.model()

    model_index = model.index(0, column_to_check, QModelIndex())

    setResult = model.setData(model_index, ip_user_input, Qt.EditRole)
    assert setResult is expected_set_result

    # if expected_set_result is True:
    #     print("ip:", model.datalineList[0]["ipOwn"], ip_user_input)
