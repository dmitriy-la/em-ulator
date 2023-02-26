import pytest

dataline_title_1 = "serv"
dataline_title_2 = "client"
str_initial_dataline_settings_list = """[{"title": "serv",
                                "protocolType": "TCP-server",
                                 "ipOwn": "127.0.0.1",
                                 "portOwn": 2048,
                                 "ipSend": "127.0.0.1",
                                 "portSend": 2050,
                                 "toutMs": 3000,
                                 "repeats": 2,
                                 "delay": 100,
                                 "sendMode": "send to all clients"},
                                {"title": "client",
                                 "protocolType": "TCP-client",
                                 "ipOwn": "127.0.0.1",
                                 "portOwn": 2050,
                                 "ipSend": "127.0.0.1",
                                 "portSend": 2048,
                                 "toutMs": 3000,
                                 "repeats": 2,
                                 "delay": 100,
                                 "sendMode": "send to all clients"}]"""
initial_dataline_1_settings = {"title": dataline_title_1,
                                "protocolType": "TCP-server",
                                 "ipOwn": "127.0.0.1",
                                 "portOwn": 2048,
                                 "ipSend": "127.0.0.1",
                                 "portSend": 2050,
                                 "toutMs": 3000,
                                 "repeats": 2,
                                 "delay": 100,
                                 "sendMode": "send to all clients"}
initial_dataline_2_settings = {"title": dataline_title_2,
                                 "protocolType": "TCP-client",
                                 "ipOwn": "127.0.0.1",
                                 "portOwn": 2050,
                                 "ipSend": "127.0.0.1",
                                 "portSend": 2048,
                                 "toutMs": 3000,
                                 "repeats": 2,
                                 "delay": 100,
                                 "sendMode": "send to all clients"}
initial_dataline_settings_list = [initial_dataline_1_settings,
                                  initial_dataline_2_settings]
@pytest.fixture
def mocker_dataline_settings_file_with_two_datalines(mocker):
    mock_dataline_file = mocker.mock_open(read_data=str_initial_dataline_settings_list)
    builtin_open = "builtins.open"
    mocker.patch(builtin_open, mock_dataline_file)

    return mock_dataline_file