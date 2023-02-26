import pytest

str_initial_modes_list_file = """[
                                    {
                                        "modeTitle": "initMode",
                                        "condList": [
                                            {
                                                "condTitle": "3 sec aftr strt",
                                                "actionsAssignedToCond": [
                                                    "send test status req"
                                                ]
                                            },
                                            {
                                                "condTitle": "received test msg status request",
                                                "actionsAssignedToCond": [
                                                    "assign READY to received msg and send",
                                                    "switch to workMode"
                                                ]
                                            },
                                            {
                                                "condTitle": "received reset to init msg",
                                                "actionsAssignedToCond": []
                                            },
                                            {
                                                "condTitle": "recv 3 triggers",
                                                "actionsAssignedToCond": []
                                            },
                                            {
                                                "condTitle": "5 secs after sending test status req",
                                                "actionsAssignedToCond": []
                                            },
                                            {
                                                "condTitle": "3s after any recv any trigger1",
                                                "actionsAssignedToCond": []
                                            }
                                        ]
                                    },
                                    {
                                        "modeTitle": "workMode",
                                        "condList": [
                                            {
                                                "condTitle": "3 sec aftr strt",
                                                "actionsAssignedToCond": []
                                            },
                                            {
                                                "condTitle": "received test msg status request",
                                                "actionsAssignedToCond": []
                                            },
                                            {
                                                "condTitle": "received reset to init msg",
                                                "actionsAssignedToCond": []
                                            },
                                            {
                                                "condTitle": "recv 3 triggers",
                                                "actionsAssignedToCond": [
                                                    "send 2 responses",
                                                    "switch to altWorkMode"
                                                ]
                                            },
                                            {
                                                "condTitle": "5 secs after sending test status req",
                                                "actionsAssignedToCond": []
                                            },
                                            {
                                                "condTitle": "3s after any recv any trigger1",
                                                "actionsAssignedToCond": []
                                            }
                                        ]
                                    }
                                ]"""
initial_modes_list = [
                            {
                                "modeTitle": "initMode",
                                "condList": [
                                    {
                                        "condTitle": "3 sec aftr strt",
                                        "actionsAssignedToCond": [
                                            "send test status req"
                                        ]
                                    },
                                    {
                                        "condTitle": "received test msg status request",
                                        "actionsAssignedToCond": [
                                            "assign READY to received msg and send",
                                            "switch to workMode"
                                        ]
                                    },
                                    {
                                        "condTitle": "received reset to init msg",
                                        "actionsAssignedToCond": []
                                    },
                                    {
                                        "condTitle": "recv 3 triggers",
                                        "actionsAssignedToCond": []
                                    },
                                    {
                                        "condTitle": "5 secs after sending test status req",
                                        "actionsAssignedToCond": []
                                    },
                                    {
                                        "condTitle": "3s after any recv any trigger1",
                                        "actionsAssignedToCond": []
                                    }
                                ]
                            },
                            {
                                "modeTitle": "workMode",
                                "condList": [
                                    {
                                        "condTitle": "3 sec aftr strt",
                                        "actionsAssignedToCond": []
                                    },
                                    {
                                        "condTitle": "received test msg status request",
                                        "actionsAssignedToCond": []
                                    },
                                    {
                                        "condTitle": "received reset to init msg",
                                        "actionsAssignedToCond": []
                                    },
                                    {
                                        "condTitle": "recv 3 triggers",
                                        "actionsAssignedToCond": [
                                            "send 2 responses",
                                            "switch to altWorkMode"
                                        ]
                                    },
                                    {
                                        "condTitle": "5 secs after sending test status req",
                                        "actionsAssignedToCond": []
                                    },
                                    {
                                        "condTitle": "3s after any recv any trigger1",
                                        "actionsAssignedToCond": []
                                    }
                                ]
                            }
                        ]
@pytest.fixture
def mocker_modes_list_file(mocker):
    mock_modes_list_file = mocker.mock_open(read_data=str_initial_modes_list_file)
    builtin_open = "builtins.open"
    mocker.patch(builtin_open, mock_modes_list_file)

    return mock_modes_list_file