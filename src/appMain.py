import configparser
import os
import sys

import PyQt5.Qt
import PyQt5.QtGui.QIcon

import src.windows.windowProfileSelect as windowProfileSelect


def datalineSettingsFileExists() -> bool:
    datalineSettingsPathfile = './__profiles__/' + profileTitle + '/datalineSettings.json'

    try:
        with open(datalineSettingsPathfile, 'r'):
            return True
    except IOError:
        print('ERROR locating dataline settings filepath!')
        return False


def msgFormatsFileExists() -> bool:
    msgFormatsPathfile = './__profiles__/' + profileTitle + '/msgFormats.json'

    try:
        with open(msgFormatsPathfile, 'r'):
            return True
    except IOError:
        print('ERROR locating message formats filepath!')
        return False


def addSectionForCurrentProfile() -> None:
    global configFile
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


if __name__ == '__main__':
    app = PyQt5.Qt.QApplication(sys.argv)

    app.setApplicationName('Em-ulator')
    app.setOrganizationName('DSL')
    app.setWindowIcon(PyQt5.QtGui.QIcon('../icons/app-icon.png'))

    config = configparser.ConfigParser()

    profileTitle = getCurrentProfileTitle()

    ex = windowProfileSelect.WindowProfileSelect()

    if profileTitle == '':
        ex.show()
        ex.exec()
    elif datalineSettingsFileExists() and msgFormatsFileExists():
        ex.startProfile(profileTitle)
        ex.close()

    sys.exit(app.exec_())
