import src.managers.ioManager as ioManager


class ManagerAutoresponseSettings(ioManager.IoManager):
    def __init__(self, profileTitle: str):
        super().__init__(profileTitle)

        self.actionList = self.readActionListFromFile()
        self.conditionList = self.readConditionListFromFile()
        self.listOfAllAutorespModes = self.readAllAutorespModesListFromFile()


    def readActionListFromFile(self) -> list:
        actionListFilePath = self._getActionListFilePath()

        actionList = self._readJsonFileByFilePath(actionListFilePath)

        self.actionList = actionList

        return actionList


    def _getActionListFilePath(self):
        actionListFilePath = './__profiles__/' + self.profileTitle + '/actionList.json'
        return actionListFilePath


    def readConditionListFromFile(self) -> list:
        conditionListFilePath = self._getConditionListFilePath()

        conditionList = self._readJsonFileByFilePath(conditionListFilePath)

        self.conditionList = conditionList

        return conditionList


    def _getConditionListFilePath(self):
        conditionListFilePath = './__profiles__/' + self.profileTitle + '/conditionList.json'
        return conditionListFilePath


    def readAllAutorespModesListFromFile(self) -> list:
        autorespModesFilePath = self._getAutorespModesFilePath()

        autorespModeslist = self._readJsonFileByFilePath(autorespModesFilePath)

        if not autorespModeslist:
            defaultModeDict = {"modeTitle": "initMode", "condList": []}
            autorespModeslist = [defaultModeDict]

        self.listOfAllAutorespModes = autorespModeslist

        return autorespModeslist


    def _getAutorespModesFilePath(self):
        autorespModesFilePath = './__profiles__/' + self.profileTitle + '/autorespModes.json'
        return autorespModesFilePath


    def getConditionDescrsList(self) -> list:
        return self.conditionList


    def getAllConditionTitlesList(self) -> list:
        allConditionTitlesList = self._getListOfAllValuesInKey("condTitle")
        return allConditionTitlesList


    def addCondition(self, newConditionDict: dict) -> None:
        self._dataList = self.conditionList

        self.addItemToDataList(newConditionDict)


    def removeCondition(self, condTitleToRemove: str) -> None:
        self.removeConditionFromModesList(condTitleToRemove)
        self.removeConditionFromConditionsList(condTitleToRemove)


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
        conditionListFilePath = self._getConditionListFilePath()

        self._dumpDataToFile(condList, conditionListFilePath)


    def getActionDescrsList(self) -> list:
        return self.actionList


    def getAllActionTitlesList(self) -> list:
        allActionTitlesList = [actionDescr["actionTitle"] for actionDescr in self.actionList]
        return allActionTitlesList


    def addAction(self, newActionDict: dict) -> None:
        self._dataList = self.actionList

        self.addItemToDataList(newActionDict)


    def removeAction(self, actionTitleToDelete: str) -> None:
        self._removeActionFromActionList(actionTitleToDelete)
        self._removeActionFromModesList(actionTitleToDelete)


    def _removeActionFromActionList(self, actionTitleToRemove: str) -> None:
        self._dataList = self.actionList

        self._removeItemFromDataListByValueInKey(actionTitleToRemove, 'actionTitle')

        self.updateActionListFile(self.actionList)


    def _removeActionFromModesList(self, actionTitleToDelete: str) -> None:
        modeTitles = self.getListOfAutorespModesTitles()

        for mode in modeTitles:
            self._removeActionFromMode(actionTitleToDelete, mode)

        self.updateModesList(self.listOfAllAutorespModes)


    def _removeActionFromMode(self, actionTitleToDelete: str, modeTitle: str) -> None:
        condListMode = self.getCondListOfMode(modeTitle)

        for cond in condListMode:
            listOfAssignedActions = cond['actionsAssignedToCond']
            self._removeActionFromCondition(actionTitleToDelete, listOfAssignedActions)


    def _removeActionFromCondition(self, actionTitleToDelete: str, listOfAssignedActions: list) -> None:
        for action in listOfAssignedActions:
            if action == actionTitleToDelete:
                listOfAssignedActions.remove(action)


    def updateActionListFile(self, actionList: list) -> None:
        actionListFilePath = self._getActionListFilePath()

        self._dumpDataToFile(actionList, actionListFilePath)


    def getCondListOfMode(self, modeTitle: str) -> list:
        self._dataList = self.listOfAllAutorespModes

        mode = self._getItemByValueInKey(modeTitle, 'modeTitle')

        if mode is None:
            return []
        else:
            return mode['condList']


    def getAllAutorespModesList(self) -> list:
        return self.listOfAllAutorespModes


    def getListOfAutorespModesTitles(self) -> list:
        self._dataList = self.listOfAllAutorespModes

        modeTitlesList = self._getListOfAllValuesInKey('modeTitle')

        return modeTitlesList


    def removeModeFromAutorespModesList(self, modeTitleToRemove: str) -> None:
        self._dataList = self.listOfAllAutorespModes

        self._removeItemFromDataListByValueInKey(modeTitleToRemove, 'modeTitle')

        self.updateModesList(self.listOfAllAutorespModes)


    def updateModesList(self, newModesList: list):
        autorespModesFilePath = self._getAutorespModesFilePath()
        self._dumpDataToFile(newModesList, autorespModesFilePath)
