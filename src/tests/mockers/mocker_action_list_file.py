import pytest

str_initial_action_list_file = """
                                [
                                    {
                                        "actionTitle": "send test status req",
                                        "actionType": "actionTypeRespondWithNamedMsg",
                                        "listOfMsgToRespondWith": [
                                            "test_status_req"
                                        ]
                                    },
                                    {
                                        "actionTitle": "assign READY to received msg and send",
                                        "actionType": "actionTypeRespondWithReceivedMsgWithAssigningFields",
                                        "listOfFieldTitlesAndValuesToReplaceWhenRespondingWithReceivedMsg": [
                                            {
                                                "fieldTitle": "test_status",
                                                "fieldValue": "000A"
                                            }
                                        ]
                                    },
                                    {
                                        "actionTitle": "send 2 responses",
                                        "actionType": "actionTypeRespondWithFewNamedMsg",
                                        "listOfMsgToRespondWith": [
                                            "response_ZEROED",
                                            "response_all_4"
                                        ]
                                    },
                                    {
                                        "actionTitle": "send trigger 2 bbbb",
                                        "actionType": "actionTypeRespondWithNamedMsg",
                                        "listOfMsgToRespondWith": [
                                            "trigger2_bbbb"
                                        ]
                                    },
                                    {
                                        "actionTitle": "switch to initMode",
                                        "actionType": "actionTypeChangeMode",
                                        "newMode": "initMode"
                                    },
                                    {
                                        "actionTitle": "switch to workMode",
                                        "actionType": "actionTypeChangeMode",
                                        "newMode": "workMode"
                                    },
                                    {
                                        "actionTitle": "switch to altWorkMode",
                                        "actionType": "actionTypeChangeMode",
                                        "newMode": "altWorkMode"
                                    }
                                ]"""
action_send_test = {"actionTitle": "send test status req",
                    "actionType": "actionTypeRespondWithNamedMsg",
                    "listOfMsgToRespondWith": ["test_status_req"]}
action_assign_ready = {"actionTitle": "assign READY to received msg and send",
                       "actionType": "actionTypeRespondWithReceivedMsgWithAssigningFields",
                       "listOfFieldTitlesAndValuesToReplaceWhenRespondingWithReceivedMsg": [{"fieldTitle": "test_status",
                                                                                             "fieldValue": "000A"}]}
action_send_two_responses = {"actionTitle": "send 2 responses",
                             "actionType": "actionTypeRespondWithFewNamedMsg",
                             "listOfMsgToRespondWith": ["response_ZEROED", "response_all_4"]}
action_send_trigger_two = {"actionTitle": "send trigger 2 bbbb",
                           "actionType": "actionTypeRespondWithNamedMsg",
                           "listOfMsgToRespondWith": ["trigger2_bbbb"]}
action_switch_to_init = {"actionTitle": "switch to initMode",
                           "actionType": "actionTypeChangeMode",
                           "newMode": "initMode"}
action_switch_to_work = {"actionTitle": "switch to workMode",
                         "actionType": "actionTypeChangeMode",
                         "newMode": "workMode"}
action_switch_to_alt_work = {"actionTitle": "switch to altWorkMode",
                             "actionType": "actionTypeChangeMode",
                             "newMode": "altWorkMode"}
initial_action_list = [action_send_test,
                       action_assign_ready,
                       action_send_two_responses,
                       action_send_trigger_two,
                       action_switch_to_init,
                       action_switch_to_work,
                       action_switch_to_alt_work]
@pytest.fixture
def mocker_action_list_file(mocker):
    mock_condition_list_file = mocker.mock_open(read_data=str_initial_action_list_file)
    builtin_open = "builtins.open"
    mocker.patch(builtin_open, mock_condition_list_file)

    return mock_condition_list_file