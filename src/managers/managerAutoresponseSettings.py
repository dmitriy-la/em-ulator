import json


class ManagerAutoresponseSettings(object):
    def __init__(self, profileTitle: str):
        self.profileTitle = profileTitle

        self.conditionListFilePath = './__profiles__/' + profileTitle + '/conditionList.json'
        self.actionListFilePath = './__profiles__/' + profileTitle + '/actionList.json'
        self.autorespModesFilePath = './__profiles__/' + profileTitle + '/autorespModes.json'

        self.conditionList = self.readConditionListFromFile()
        self.actionDescrsList = self.readActionListFromFile()
        self.listOfAllAutorespModes = self.readAllAutorespModesListFromFile()


    def readConditionListFromFile(self) -> list:
        conditionList = list()

        try:
            with open(self.conditionListFilePath, 'r', newline='', encoding='koi8-r') as condListFile:
                conditionList = json.load(condListFile)
        except IOError:
            with open(self.conditionListFilePath, 'a') as condListFile:
                json.dump([], condListFile, indent=4, ensure_ascii=False)
        except json.decoder.JSONDecodeError:
            with open(self.conditionListFilePath, 'a') as condListFile:
                json.dump([], condListFile, indent=4, ensure_ascii=False)

        self.conditionList = conditionList

        return conditionList


    def readActionListFromFile(self) -> list:
        actionList = []

        try:
            with open(self.actionListFilePath, 'r', newline='', encoding='koi8-r') as actionListFile:
                actionList = json.load(actionListFile)
        except IOError:
            with open(self.actionListFilePath, 'a') as actionListFile:
                json.dump([], actionListFile, indent=4, ensure_ascii=False)
        except json.decoder.JSONDecodeError:
            with open(self.actionListFilePath, 'a') as actionListFile:
                json.dump([], actionListFile, indent=4, ensure_ascii=False)

        self.actionDescrsList = actionList

        return actionList


    def readAllAutorespModesListFromFile(self) -> list:
        defaultModeDict = { "modeTitle": "initMode",
                            "condList":  [] }
        autorespModeslist = [defaultModeDict]

        try:
            with open(self.autorespModesFilePath, 'r', newline='', encoding='koi8-r') as autorespModesFile:
                autorespModeslist = json.load(autorespModesFile)
        except IOError:
            with open(self.autorespModesFilePath, 'a') as autorespModesFile:
                json.dump([], autorespModesFile, indent=4, ensure_ascii=False)
        except json.decoder.JSONDecodeError:
            with open(self.autorespModesFilePath, 'a') as autorespModesFile:
                json.dump([], autorespModesFile, indent=4, ensure_ascii=False)

        self.listOfAllAutorespModes = autorespModeslist

        return autorespModeslist


    def getConditionList(self) -> list:
        return self.conditionList


    def getAllConditionTitlesList(self) -> list:
        allConditionTitlesList = [condDescr["condTitle"] for condDescr in self.conditionList]
        return allConditionTitlesList


    def addCondition(self, newConditionDict: dict) -> None:
        self.conditionList.append(newConditionDict)
        self.updateConditionListFile(self.conditionList)


    def removeCondition(self, condTitleToDelete: str) -> None:
        self.removeConditionFromModesList(condTitleToDelete)
        self.removeConditionFromConditionsList(condTitleToDelete)


    def removeConditionFromModesList(self, condTitleToDelete: str) -> None:
        modeTitles = self.getListOfAutorespModesTitles()

        for modeTitle in modeTitles:
            condListForMode = self.getCondListOfMode(modeTitle)

            for cond in condListForMode:
                if cond['condTitle'] == condTitleToDelete:
                    condListForMode.remove(cond)

        self.updateModesList(self.listOfAllAutorespModes)


    def removeConditionFromConditionsList(self, condTitleToDelete: str) -> None:
        for cond in self.conditionList:
            if cond['condTitle'] == condTitleToDelete:
                self.conditionList.remove(cond)

                self.updateConditionListFile(self.conditionList)


    def updateConditionListFile(self, condList: list) -> None:
        with open(self.conditionListFilePath, 'w', newline='', encoding='koi8-r') as condListFile:
            json.dump(condList, condListFile, indent=4, ensure_ascii=False)


    def getActionDescrsList(self) -> list:
        return self.actionDescrsList


    def getAllActionTitlesList(self) -> list:
        allActionTitlesList = [actionDescr["actionTitle"] for actionDescr in self.actionDescrsList]
        return allActionTitlesList


    def addAction(self, newActionDict: dict) -> None:
        self.actionDescrsList.append(newActionDict)
        self.updateActionListFile(self.actionDescrsList)


    def removeAction(self, actionTitleToDelete: str) -> None:
        self.removeActionFromActionList(actionTitleToDelete)
        self.removeActionFromModesList(actionTitleToDelete)


    def removeActionFromActionList(self, actionTitleToDelete: str) -> None:
        for action in self.actionDescrsList:
            if action['actionTitle'] == actionTitleToDelete:
                self.actionDescrsList.remove(action)
                self.updateActionListFile(self.actionDescrsList)


    def removeActionFromModesList(self, actionTitleToDelete: str) -> None:
        modeTitles = self.getListOfAutorespModesTitles()

        for mode in modeTitles:
            self.removeActionFromMode(actionTitleToDelete, mode)

        self.updateModesList(self.listOfAllAutorespModes)


    def removeActionFromMode(self, actionTitleToDelete: str, modeTitle: str) -> None:
        condListMode = self.getCondListOfMode(modeTitle)

        for cond in condListMode:
            listOfAssignedActions = cond['actionsAssignedToCond']
            self.removeActionFromCondition(actionTitleToDelete, listOfAssignedActions)


    def removeActionFromCondition(self, actionTitleToDelete: str, listOfAssignedActions: list) -> None:
        for action in listOfAssignedActions:
            if action == actionTitleToDelete:
                listOfAssignedActions.remove(action)


    def updateActionListFile(self, actionList: list) -> None:
        with open(self.actionListFilePath, 'w', newline='', encoding='koi8-r') as actionListFile:
            json.dump(actionList, actionListFile, indent=4, ensure_ascii=False)


    def getCondListOfMode(self, modeTitle: str) -> list:
        condList = []

        for mode in self.listOfAllAutorespModes:
            if mode['modeTitle'] == modeTitle:
                condList = mode['condList']
                break

        return condList


    def getAllAutorespModesList(self) -> list:
        return self.listOfAllAutorespModes


    def getListOfAutorespModesTitles(self) -> list:
        modeTitlesList = []

        for mode in self.listOfAllAutorespModes:
            modeTitlesList.append(mode['modeTitle'])

        return modeTitlesList


    def removeModeFromAutorespModesList(self, modeTitleToDelete: str) -> None:
        for mode in self.listOfAllAutorespModes:
            if mode['modeTitle'] == modeTitleToDelete:
                self.listOfAllAutorespModes.remove(mode)
                self.updateModesList(self.listOfAllAutorespModes)
                break


    def updateModesList(self, modesList: list) -> None:
        with open(self.autorespModesFilePath, 'w', newline='', encoding='koi8-r') as autorespModesFile:
            json.dump(modesList, autorespModesFile, indent=4, ensure_ascii=False)
