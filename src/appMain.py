import configparser
import gettext
import os
import pathlib
import sys

import PyQt5.Qt
import PyQt5.QtGui

import src.managers.managerDatalineSettings as managerDatalineSettings
import src.ui.windows.windowProfileSelect as windowProfileSelect

import threads.threadTcpClient as threadTcpClient
import threads.threadTcpServer as threadTcpServer
import threads.threadUdp as threadUdp

_ = gettext.gettext


def datalineSettingsFileExists(profileTitle: str) -> bool:
    datalineSettingsPathfile = './__profiles__/' + profileTitle + '/datalineSettings.json'

    try:
        with open(datalineSettingsPathfile, 'r'):
            print("OK, found dataline settings file...")
            return True
    except IOError:
        print(_('ERROR locating dataline settings file in: ') + str(pathlib.Path.cwd().resolve()) +
              _(', it should be in subfolder: ') + datalineSettingsPathfile[1:])
        return False


def msgFormatsFileExists(profileTitle: str) -> bool:
    msgFormatsPathfile = './__profiles__/' + profileTitle + '/msgFormats.json'

    try:
        with open(msgFormatsPathfile, 'r'):
            print("OK, found message formats file...")
            return True
    except IOError:
        print(_('ERROR locating message formats file in: ') + str(pathlib.Path.cwd().resolve()) +
              _(', it should be in subfolder: ') + msgFormatsPathfile[1:])
        return False


def addSectionForCurrentProfile() -> None:
    config = configparser.ConfigParser()

    with open('settings.ini', 'a') as configFile:
        if not config.has_section('current_profile'):
            config.add_section('current_profile')

        config.set('current_profile', 'profile_title', '')
        config.write(configFile)


def recreateSettingsFile() -> None:
    if os.path.exists('settings.ini'):
        os.remove('settings.ini')
    addSectionForCurrentProfile()


def getCurrentProfileTitle() -> str:
    """
    Retrieving profile title from settings.ini file in project's folder.
    :return:
    """
    config = configparser.ConfigParser()

    profileTitle = ''

    try:
        with open('settings.ini', 'r'):
            config.read('settings.ini')

            if not config.has_section('current_profile'):
                addSectionForCurrentProfile()

            profileTitle = config.get('current_profile', 'profile_title')
    except IOError:
        recreateSettingsFile()
    except configparser.NoOptionError:
        recreateSettingsFile()
    except configparser.NoSectionError:
        recreateSettingsFile()
    except configparser.ParsingError:
        recreateSettingsFile()

    return profileTitle


def startInGuiMode():
    print("Starting in GUI mode")

    app = PyQt5.Qt.QApplication(sys.argv)

    app.setApplicationName('Em-ulator')
    app.setOrganizationName('DSL')
    app.setWindowIcon(PyQt5.QtGui.QIcon('../icons/app-icon.png'))

    profileTitle = getCurrentProfileTitle()
    ex = windowProfileSelect.WindowProfileSelect()

    if profileTitle == '':
        ex.show()
        ex.exec()
    elif datalineSettingsFileExists(profileTitle) and msgFormatsFileExists(profileTitle):
        ex.startProfile(profileTitle)
        ex.close()

    return app


def getCurrentProfileTitleFromCommandLineArgs() -> str:
    if len(sys.argv) > 1:
        profileTitle = [sys.argv[1]]
    else:
        profileTitle = ''

    return profileTitle


def startInCommandLineMode():
    print("Starting in command line mode")
    app = PyQt5.Qt.QCoreApplication(sys.argv)

    profileTitle = getCurrentProfileTitleFromCommandLineArgs()

    if datalineSettingsFileExists(profileTitle) and msgFormatsFileExists(profileTitle):
        datalineSettingsManager = managerDatalineSettings.ManagerDatalineSettings(profileTitle)
        datalineList = datalineSettingsManager.getDataList()

        for dataline in datalineList:
            if dataline["protocolType"] == 'TCP-server':
                networkThread = threadTcpServer.ThreadTcpServer(dataline)
                print('Started TCP-server.')
            elif dataline["protocolType"] == 'TCP-client':
                networkThread = threadTcpClient.ThreadTcpClient(dataline)
                print('Started TCP-client.')
            elif dataline["protocolType"] == 'UDP':
                networkThread = threadUdp.ThreadUdp(dataline)
                print('Started UDP.')
            elif dataline["protocolType"] == 'raw':
                networkThread = threadUdp.ThreadUdp(dataline)
                print('Started UDP-raw.')
            else:
                networkThread = threadUdp.ThreadUdp(dataline)
                print('Started UDP.')

            networkThread.start()
    else:
        print(_("Unable to find necessary settings files in ./__profiles__/") + profileTitle + "/ folder")
        print(_("Does it even exist?.."))
        print(_("Shutting down."))

    return app


if __name__ == '__main__':
    useGUI = '-no-gui' not in sys.argv
    if useGUI:
        app = startInGuiMode()
    else:
        app = startInCommandLineMode()

    sys.exit(app.exec_())
