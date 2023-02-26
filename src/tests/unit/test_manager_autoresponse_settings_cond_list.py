import src.managers.managerAutoresponseSettings
from src.tests.mockers.mocker_cond_list_file import mocker_condition_list_file, initial_condition_list


TEST_PROFILE_STR = "test_profile"


def test_working_with_condition_list(mocker_condition_list_file):
    managerAutoresponseSettings = src.managers.managerAutoresponseSettings.ManagerAutoresponseSettings(TEST_PROFILE_STR)
    cond_list = managerAutoresponseSettings.readConditionListFromFile()
    assert cond_list == initial_condition_list

    first_condition_title = "10 sec after start"
    first_new_condition = {"condTitle": first_condition_title,
                           "condType": "condTypeTimePassedAfterStart",
                           "condTimeMs": 10000}
    managerAutoresponseSettings.addCondition(first_new_condition)
    initial_condition_list.append(first_new_condition)
    current_condition_list = managerAutoresponseSettings.getConditionDescrsList()
    assert current_condition_list == initial_condition_list

    initial_condition_list.remove(first_new_condition)
    managerAutoresponseSettings.removeCondition(first_condition_title)
    assert current_condition_list == initial_condition_list

    second_new_condition = {"condTitle": "777 sec after start",
                            "condType": "condTypeTimePassedAfterStart",
                            "condTimeMs": 777000}
    managerAutoresponseSettings.addCondition(second_new_condition)
    initial_condition_list.append(second_new_condition)
    assert current_condition_list == initial_condition_list
