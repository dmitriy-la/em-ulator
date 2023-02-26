import pytest

str_initial_condition_list_file = """[
    {
        "condTitle": "3 sec aftr strt",
        "condType": "condTypeTimePassedAfterStart",
        "condTimeMs": 3000
    },
    {
        "condTitle": "received test msg status request",
        "condType": "condTypeReceivedSingleMsg",
        "condRegexpTitlesList": [
            "test_msg_status_req"
        ]
    },
    {
        "condTitle": "received reset to init msg",
        "condType": "condTypeReceivedSingleMsg",
        "condRegexpTitlesList": [
            "reset_to_init_msg"
        ]
    },
    {
        "condTitle": "recv 3 triggers",
        "condType": "condTypeReceivedFewMsg",
        "condRegexpTitlesList": [
            "any_trigger1",
            "trgr2_1111",
            "trgr2_cccc"
        ]
    },
    {
        "condTitle": "5 secs after sending test status req",
        "condType": "condTypeTimePassedAfterSendMsg",
        "condTimeMs": 5000,
        "condRegexpTitlesList": [
            "test_status_req"
        ]
    },
    {
        "condTitle": "3s after any recv any trigger1",
        "condType": "condTypeTimePassedAfterReceivingMsg",
        "condTimeMs": 3000,
        "condRegexpTitlesList": [
            "any_trigger1"
        ]
    }
]"""

cond_after_start = {"condTitle": "3 sec aftr strt",
                    "condType": "condTypeTimePassedAfterStart",
                    "condTimeMs": 3000}
cond_received_msg_test = {"condTitle": "received test msg status request",
                          "condType": "condTypeReceivedSingleMsg",
                          "condRegexpTitlesList": ["test_msg_status_req"]}
cond_received_reset = {"condTitle": "received reset to init msg",
                       "condType": "condTypeReceivedSingleMsg",
                       "condRegexpTitlesList": ["reset_to_init_msg"]}
cond_received_three_triggers = {"condTitle": "recv 3 triggers",
                                "condType": "condTypeReceivedFewMsg",
                                "condRegexpTitlesList": ["any_trigger1", "trgr2_1111", "trgr2_cccc"]}
cond_time_after_send = {"condTitle": "5 secs after sending test status req",
                        "condType": "condTypeTimePassedAfterSendMsg",
                        "condTimeMs": 5000,
                        "condRegexpTitlesList": ["test_status_req"]}
cond_time_after_recv = {"condTitle": "3s after any recv any trigger1",
                        "condType": "condTypeTimePassedAfterReceivingMsg",
                        "condTimeMs": 3000,
                        "condRegexpTitlesList": ["any_trigger1"]}

initial_condition_list = [cond_after_start,
                          cond_received_msg_test,
                          cond_received_reset,
                          cond_received_three_triggers,
                          cond_time_after_send,
                          cond_time_after_recv]
@pytest.fixture
def mocker_condition_list_file(mocker):
    mock_condition_list_file = mocker.mock_open(read_data=str_initial_condition_list_file)
    builtin_open = "builtins.open"
    mocker.patch(builtin_open, mock_condition_list_file)

    return mock_condition_list_file