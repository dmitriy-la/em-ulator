import sys

from PyQt5.QtWidgets import QApplication

import src.windows.windowProfileSelect


def test_window_profile_select(mocker):
    test_app = QApplication(sys.argv)

    mocker.patch('src.windows.windowProfileSelect.WindowProfileSelect.getListOfAvailableProfiles', return_value=[])

    winProfileSelect = src.windows.windowProfileSelect.WindowProfileSelect()
    assert (winProfileSelect.comboBoxListWithProfiles.count, 4)

    winProfileSelect = src.windows.windowProfileSelect.WindowProfileSelect()

    assert (winProfileSelect.comboBoxListWithProfiles.count, 1)
