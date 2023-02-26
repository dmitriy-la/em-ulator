import src.managers.managerAutoresponseSettings
from src.tests.mockers.mocker_action_list_file import initial_action_list, mocker_action_list_file


TEST_PROFILE_STR = "test_profile"


def test_working_with_action_list(mocker_action_list_file):
    """
    Testing adding and removing actions
    """

    managerAutoresponseSettings = src.managers.managerAutoresponseSettings.ManagerAutoresponseSettings(TEST_PROFILE_STR)
    current_action_list = managerAutoresponseSettings.readActionListFromFile()
    assert current_action_list == initial_action_list

    first_action_title = "first new action"
    first_new_action = {"actionTitle": first_action_title,
                        "actionType": "actionTypeChangeMode",
                        "newMode": "workMode"}
    managerAutoresponseSettings.addAction(first_new_action)
    initial_action_list.append(first_new_action)
    current_action_list = managerAutoresponseSettings.getActionDescrsList()
    assert current_action_list == initial_action_list

    initial_action_list.remove(first_new_action)
    managerAutoresponseSettings.removeAction(first_action_title)
    assert current_action_list == initial_action_list

    second_action_title = "second new action"
    second_new_action = {"actionTitle": second_action_title,
                         "actionType": "actionTypeChangeMode",
                         "newMode": "random Mode"}
    managerAutoresponseSettings.addAction(second_new_action)
    initial_action_list.append(second_new_action)
    assert current_action_list == initial_action_list
