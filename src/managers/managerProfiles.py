import os
import shutil
from configparser import ConfigParser


class ManagerProfiles(object):
    def __init__(self, profileTitle='default'):
        self.profileTitle = profileTitle
        self.profileFilePath = ''
        self.msgFormatsFilePath = ''
        self.datalineSettingsFilePath = ''
        self.generalProfileSettings = ''

        if profileTitle != '':
            self.setCurrentProfile(self.profileTitle)


    def setCurrentProfile(self, profileTile: str) -> None:
        """
        Setting up data (paths to profile files) for current profile
        :param profileTile:
        :return:
        """
        self.profileTitle = profileTile
        self.profileFilePath = './__profiles__/' + profileTile + '/'
        self.msgFormatsFilePath = self.profileFilePath + 'msgFormats.json'
        self.datalineSettingsFilePath = self.profileFilePath + 'datalineSettings.json'

        self.generalProfileSettings = self.profileFilePath + 'profile.ini'


    def addEmptyProfile(self, profileTitle='') -> bool:
        """
        Creating directory and files for newly created profile
        :param profileTitle:
        :return:
        """
        result = False

        if profileTitle != '':
            self.setCurrentProfile(profileTitle)

        try:
            os.makedirs(self.profileFilePath)
            self.createInitFileForAllowingImportFromProfileDir()
            self.createCalcCrcFileForProfile()
            self.createHandlerRawMsgFileForProfile()

            result = True
        except FileExistsError:
            print('Error: profile directory already exists.')
        except IOError:
            print('Error creating __init__ profile files!')

        self.setMaskForFormingReceiptType('')
        self.setSendMode('parallel')

        return result


    def createInitFileForAllowingImportFromProfileDir(self) -> None:
        """
        Creating __init__.py so that other files in profile directory can be used as modules
        :return:
        """
        initFile = open(self.profileFilePath + '__init__.py', 'w+')
        initFile.write("")
        initFile.close()


    def createCalcCrcFileForProfile(self) -> None:
        """
        Creating default file with script that counts control sums in messages.
        Returns zeroes by default, and supposed to be modified later by user in accordance to the
        algorithm used for getting control sums.
        :return:
        """
        filename = self.profileFilePath + 'calcCrc.py'

        emptyCalcCrcFile = open(filename, "w+")

        emptyCalcCrcFile.write("def calcCrc(self, msg: str):\n"
                               "    # Method that calculates control sum in message for current profile\n"
                               "    crc = '00000000000000000000000000000000'\n"
                               "    return crc\n")
        emptyCalcCrcFile.close()


    def createHandlerRawMsgFileForProfile(self) -> None:
        """
        Creating default file with script that forms UDP-level packets while using raw sockets.
        Returns unchanged message by default.
        :return:
        """
        filename = self.profileFilePath + 'handlerRawMsg.py'

        emptyCalcCrcFile = open(filename, "w+")

        emptyCalcCrcFile.write("def proccessMsgForSend(self, msg: str):\n"
                               "    # Process msg before send\n"
                               "    return msg\n\n"
                               "def proccessMsgReceived(self, msg: str):\n"
                               "    # Process msg after receive\n"
                               "    return msg\n")

        emptyCalcCrcFile.close()


    def setMaskForFormingReceiptType(self, mask='') -> None:
        """
        Set general profile parameter - receipt mask - in config file.
        Using receipt mask means that instead of one fixed hex for receipts,
        hex for receipt types are derived from message types that they are sent in response to
        by the means of bitwise AND
        :param mask:
        :return:
        """
        config = ConfigParser()

        try:
            with open(self.generalProfileSettings, 'r'):
                config.read(self.generalProfileSettings)

                formerMask = config.get('general_settings', 'mask_for_forming_receipt_type')
                if not formerMask:
                    config.add_section('general_settings')

                config.set('general_settings', 'mask_for_forming_receipt_type', mask)

            with open(self.generalProfileSettings, 'w') as configFile:
                config.write(configFile)
        except IOError:
            with open(self.generalProfileSettings, 'a') as configFile:
                config.add_section('general_settings')
                config.set('general_settings', 'mask_for_forming_receipt_type', '')
                config.set('general_settings', 'send_mode', 'parallel')
                config.write(configFile)


    def getMaskForFormingReceiptType(self) -> str:
        """
        Get general profile parameter - receipt mask - from config file
        :return:
        """
        config = ConfigParser()

        mask = ''

        if os.path.exists(self.datalineSettingsFilePath):
            with open(self.generalProfileSettings, 'r'):
                config.read(self.generalProfileSettings)
                mask = config.get('general_settings', 'mask_for_forming_receipt_type')
        else:
            with open(self.generalProfileSettings, 'a+') as configFile:
                config.add_section('general_settings')
                config.set('general_settings', 'mask_for_forming_receipt_type', '')
                config.write(configFile)

        return mask


    def setSendMode(self, mode: str) -> None:
        """
        Set general profile parameter - send mode - in config file.
        Mode can be either parallel or sequential.
        In sequential mode message cannot be sent until receipt for previously sent message is received.
        There is no such restriction in parallel mode.
        :param mode:
        :return:
        """
        config = ConfigParser()

        try:
            with open(self.generalProfileSettings, 'r'):
                config.read(self.generalProfileSettings)

                formerMode = config.get('general_settings', 'send_mode')
                if not formerMode:
                    config.add_section('general_settings')

                config.set('general_settings', 'send_mode', mode)

            with open(self.generalProfileSettings, 'w') as configFile:
                config.write(configFile)
        except IOError:
            with open(self.generalProfileSettings, 'a') as configFile:
                config.add_section('general_settings')
                config.set('general_settings', 'send_mode', mode)
                config.write(configFile)


    def getSendMode(self) -> str:
        """
        Get general profile parameter - send mode - from config file.
        :return mode:
        """
        config = ConfigParser()

        mode = ''

        try:
            with open(self.generalProfileSettings, 'r'):
                config.read(self.generalProfileSettings)
                mode = config.get('general_settings', 'send_mode')
        except IOError:
            with open(self.generalProfileSettings, 'a') as configFile:
                config.add_section('general_settings')
                config.set('general_settings', 'send_mode', '')
                config.write(configFile)

        return mode


    def removeProfile(self, profileTitle='') -> None:
        """
        Removing profile directory and its contents
        :param profileTitle:
        :return:
        """
        if profileTitle == '':
            profileDirToRemove = self.profileFilePath
        else:
            profileDirToRemove = './__profiles__/' + profileTitle + '/'
        try:
            shutil.rmtree(profileDirToRemove)
        except IOError:
            print('No profile')
