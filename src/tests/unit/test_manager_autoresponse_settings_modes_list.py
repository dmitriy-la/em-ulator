import src.managers.managerAutoresponseSettings
from src.tests.mockers.mocker_modes_list_file import mocker_modes_list_file, initial_modes_list


TEST_PROFILE_STR = "test_profile"


def test_working_with_mode_list(mocker_modes_list_file):
    managerAutoresponseSettings = src.managers.managerAutoresponseSettings.ManagerAutoresponseSettings(TEST_PROFILE_STR)
    current_mode_list = managerAutoresponseSettings.readAllAutorespModesListFromFile()
    assert current_mode_list == initial_modes_list

    first_mode_title = "first new mode"
    first_new_mode = {"modeTitle": first_mode_title,
                      "modeType": "modeTypeChangeMode",
                      "newMode": "workMode"}
    managerAutoresponseSettings.addMode(first_new_mode)
    initial_modes_list.append(first_new_mode)
    current_mode_list = managerAutoresponseSettings.getAllAutorespModesList()
    assert current_mode_list == initial_modes_list

    initial_modes_list.remove(first_new_mode)
    managerAutoresponseSettings.removeModeFromAutorespModesList(first_mode_title)
    assert current_mode_list == initial_modes_list

    second_mode_title = "second new mode"
    second_new_mode = {"modeTitle": second_mode_title,
                       "modeType": "modeTypeChangeMode",
                       "newMode": "random Mode"}
    managerAutoresponseSettings.addMode(second_new_mode)
    initial_modes_list.append(second_new_mode)
    assert current_mode_list == initial_modes_list
