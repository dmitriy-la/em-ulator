from unittest import mock

import src.managers.ioManager
import src.managers.managerDatalineSettings
from src.tests.mockers.mocker_dataline_settings import dataline_title_1, dataline_title_2
from src.tests.mockers.mocker_dataline_settings import initial_dataline_1_settings, initial_dataline_2_settings
from src.tests.mockers.mocker_dataline_settings import initial_dataline_settings_list
from src.tests.mockers.mocker_dataline_settings import mocker_dataline_settings_file_with_two_datalines

TEST_PROFILE_STR = "test_profile"


def test_get_dataline_settings_by_dataline_title(mocker_dataline_settings_file_with_two_datalines):
    managerDatalineSettings = src.managers.managerDatalineSettings.ManagerDatalineSettings(TEST_PROFILE_STR)
    datalineDescr = managerDatalineSettings.getDatalineSettingsByDatalineTitle(dataline_title_1)

    assert datalineDescr == initial_dataline_1_settings

    datalineDescr = managerDatalineSettings.getDatalineSettingsByDatalineTitle(dataline_title_2)

    assert datalineDescr == initial_dataline_2_settings


def test_get_all_dataline_settings():
    with mock.patch('src.managers.ioManager.IoManager.readDataFromFile') as dataline_settings_mock:
        dataline_settings_mock.return_value = initial_dataline_settings_list

        managerDatalineSettings = src.managers.managerDatalineSettings.ManagerDatalineSettings(TEST_PROFILE_STR)
        datalineList = managerDatalineSettings.getDataList()

        assert datalineList == initial_dataline_settings_list


edited_dataline_title = dataline_title_2
editedDatalineDescr = {"title": edited_dataline_title,
                       "protocolType": "TCP-client",
                       "ipOwn": "192.168.12.234",
                       "portOwn": 12345,
                       "ipSend": "127.0.0.1",
                       "portSend": 30001,
                       "toutMs": 7000,
                       "repeats": 8,
                       "delay": 10,
                       "sendMode": "send to all clients"}
edited_dataline_settings_list = [initial_dataline_1_settings,
                                 editedDatalineDescr]
def test_update_dataline_settings_of_single_dataline(mocker_dataline_settings_file_with_two_datalines):
    managerDatalineSettings = src.managers.managerDatalineSettings.ManagerDatalineSettings(TEST_PROFILE_STR)
    assert len(managerDatalineSettings._dataList) == 2

    with mock.patch("src.managers.ioManager.json"), \
         mock.patch("src.managers.ioManager.open", mock.mock_open()) as _open:
        managerDatalineSettings.updateDatalineSettingsOfSingleDataline(editedDatalineDescr)
        src.managers.ioManager.json.dump.assert_called_with(edited_dataline_settings_list, _open(),
                                                            ensure_ascii=False, indent=4)
