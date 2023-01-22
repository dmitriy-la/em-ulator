import re

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

import src.handlers.handlerId as handlerId
import src.handlers.handlerMsgParse as handlerMsgParse
import src.handlers.handlerString as handlerString
import src.managers.managerAutoresponseSettings as managerAutoresponseSettings
import src.managers.managerMsgFormats as managerMsgFormats
import src.managers.managerNamedMsg as managerNamedMsg
import src.managers.managerNamedRegexp as managerNamedRegexp
import src.threads.threadTimer as threadTimer


DEFAULT_AUTORESPONSE_MODE_TITLE = "initMode"


class HandlerResponse(QObject):
    signalAddListOfMsgToSendingList = pyqtSignal(list)

    def __init__(self, profileTitle: str):
        super().__init__()
        self.profileTitle = profileTitle

        self.msgParser = handlerMsgParse.HandlerMsgParse(self.profileTitle)
        self.formatManager = managerMsgFormats.ManagerMsgFormats(self.profileTitle)
        self.managerAutorespSettings = managerAutoresponseSettings.ManagerAutoresponseSettings(self.profileTitle)
        self.managerNamedRegexp = managerNamedRegexp.ManagerNamedRegexp(self.profileTitle)
        self.managerNamedMsg = managerNamedMsg.ManagerNamedMsg(self.profileTitle)

        self.listOfAllAutorespModes = self.managerAutorespSettings.getAllAutorespModesList()
        self.condDescrList = self.managerAutorespSettings.getConditionList()
        self.actionDescrList = self.managerAutorespSettings.getActionDescrsList()

        self.msgReceived = ''

        self.currentAutorespModeTitle = DEFAULT_AUTORESPONSE_MODE_TITLE

        self.listOfTimers = []

        self.currentAutorespModeData = self.getCurrentAutorespModeData(self.currentAutorespModeTitle)

        self.listOfRegexpAndReceiveFlagForNotedMsgs = []

        self.listOfRegexpAndReceiveFlagForNotedMsgs = self.getInitialListOfRegexpForNotedMsgs()

        self.outgoingMsgId = 0

        self.startTimersAfterImitStart()


    def getInitialListOfRegexpForNotedMsgs(self) -> list:
        # TODO: Into class AutorespMode
        self.listOfRegexpAndReceiveFlagForNotedMsgs = []

        listOfConditionsForMode = self.getListOfNoneEmptyConditionsForCurrentMode()
        for cond in listOfConditionsForMode:
            condTitle = cond['condTitle']
            condDescr = self.getCondDescrDictFromTitle(condTitle)
            self.appendToListOfRegexpForNotedMsgs(condDescr)
            self.appenRegexpForNotedMsgInCompositeCondIfNeeded(condDescr)

        return self.listOfRegexpAndReceiveFlagForNotedMsgs


    def appenRegexpForNotedMsgInCompositeCondIfNeeded(self, condDescr: dict) -> None:
        if condDescr['condType'] == 'condTypeCompositeCond':
            listOfCondTitlesInCompositeCond = condDescr['condTitlesList']

            for condTitle in listOfCondTitlesInCompositeCond:
                condInCompCondDescr = self.getCondDescrDictFromTitle(condTitle)
                self.appendToListOfRegexpForNotedMsgs(condInCompCondDescr)


    def appendToListOfRegexpForNotedMsgs(self, condDescr: dict) -> None:
        condRegexpTitlesList = self.getCondRegexpTitlesListFromCondDescr(condDescr)

        for regexpTitle in condRegexpTitlesList:
            regexp = self.managerNamedRegexp.getBinRegexpFromRegexpTitle(regexpTitle)

            if not self.regexpInListOfRegexpAndNotedMsgs(regexp):
                regexpForNotedMsgDict = {"regexp": regexp, "msgNoted": False}
                self.listOfRegexpAndReceiveFlagForNotedMsgs.append(regexpForNotedMsgDict)


    def regexpInListOfRegexpAndNotedMsgs(self, regexp: str) -> bool:
        for line in self.listOfRegexpAndReceiveFlagForNotedMsgs:
            if line["regexp"] == regexp:
                return True
        return False


    def getCondRegexpTitlesListFromCondDescr(self, condDescr: dict) -> list:
        if condDescr['condType'] == 'condTypeReceivedFewMsg' or \
           condDescr['condType'] == 'condTypeTimePassedAfterReceivingMsg' or \
           condDescr['condType'] == "condTypeTimePassedAfterSendMsg" or \
           condDescr['condType'] == 'condTypeReceivedSingleMsg':
            condRegexpTitlesList = condDescr["condRegexpTitlesList"]
            return condRegexpTitlesList
        else:
            return []


    def conditionIsNotEmpty(self, condInModeDescr: dict) -> bool:
        if len(condInModeDescr["actionsAssignedToCond"]) > 0:
            return True
        else:
            return False


    def getListOfMsgToSendAtStart(self) -> list:
        listOfActionsAtStart = self.getListOfActionToPerformAfterStart()
        listOfMsg = self.getListOfResponses(listOfActionsAtStart)

        return listOfMsg


    def getListOfActionToPerformAfterStart(self) -> list:
        # TODO: Into class AutorespMode
        listOfActionsToPerformAfterStart = []

        listOfConditionsForMode = self.getListOfNoneEmptyConditionsForCurrentMode()

        for cond in listOfConditionsForMode:
            condTitle = cond['condTitle']
            condDescr = self.getCondDescrDictFromTitle(condTitle)
            if self.conditionIsTriggeredAtStart(condDescr):
                actionsAssignedToCond = cond["actionsAssignedToCond"]
                listOfActionsToPerformAfterStart.extend(actionsAssignedToCond)

        return listOfActionsToPerformAfterStart


    def actionsAreAssignedToCondition(self, cond: dict) -> bool:
        if len(cond["actionsAssignedToCond"]) > 0:
            return True
        else:
            return False


    def conditionIsTriggeredAtStart(self, condDescr: dict) -> bool:
        if condDescr['condType'] == 'condTypeTimePassedAfterStart':
            if isinstance(condDescr['condTimeMs'], str) and condDescr['condTimeMs'] == '0':
                return True
        return False


    def factOfReceivingMsgShouldBeNoted(self, binMsg: str) -> bool:
        # TODO: Into class AutorespMode
        for line in self.listOfRegexpAndReceiveFlagForNotedMsgs:
            regexp = line["regexp"]
            regexp = self.prepareRegexp(regexp)

            result = re.search(regexp, binMsg)

            if result:
                return True

        return False


    def prepareRegexp(self, regexp: str) -> str:
        regexp = regexp.replace(' ', '')

        if regexp != "" and regexp[0] != '^':
            regexp = '^' + regexp

        return regexp


    def setOneOfNotedMsgsWasReceived(self, binMsg: str) -> None:
        # TODO: Into class AutorespMode
        for line in self.listOfRegexpAndReceiveFlagForNotedMsgs:
            regexp = line["regexp"]

            regexp = self.prepareRegexp(regexp)

            result = re.search(regexp, binMsg)

            if result:
                line["msgNoted"] = True
                print("msg noted")
                return


    def noteMsgIfNeeded(self, msg: str) -> None:
        stringHandler = handlerString.HandlerString()
        binMsg = stringHandler.getWholeMsgBinStrFromHexStr(msg)

        if self.factOfReceivingMsgShouldBeNoted(binMsg):
            self.setOneOfNotedMsgsWasReceived(binMsg)


    def getCurrentAutorespModeData(self, curModeTitle: str) -> dict:
        for mode in self.listOfAllAutorespModes:
            if mode['modeTitle'] == curModeTitle:
                return mode

        return {'modeTitle': "", "condList": []}


    def proccessMsgReceived(self, msg) -> list:
        msg = self.prepareMsg(msg)

        self.msgReceived = msg

        self.noteMsgIfNeeded(msg)
        self.startTimersIfNeeded()

        listOfActionTitlesTriggered = self.getListOfActionTitlesTriggeredByReceivingMsg(msg)

        if len(listOfActionTitlesTriggered) > 0:
            print("Actions triggered:", listOfActionTitlesTriggered)

        listOfResponses = self.getListOfResponses(listOfActionTitlesTriggered)

        self.changeModeIfNeeded(listOfActionTitlesTriggered)

        return listOfResponses


    def startTimersIfNeeded(self) -> None:
        listOfCondDescrsOfTypeTimePassedAfterSendOrReceive = self.getListOfCondDescrsOfTypeTimePassedAfterSendOrReceive()

        for cond in listOfCondDescrsOfTypeTimePassedAfterSendOrReceive:
            print("Processing time passed after condition...")
            condTitle = cond['condTitle']
            self.startTimerForConditionIfNeeded(condTitle)


    def startTimerForConditionIfNeeded(self, condTitle: str) -> None:
        condDescr = self.getCondDescrDictFromTitle(condTitle)

        condRegexpTitlesList = condDescr["condRegexpTitlesList"]

        for msgRegexpTitle in condRegexpTitlesList:
            msgRegexpBin = self.managerNamedRegexp.getBinRegexpFromRegexpTitle(msgRegexpTitle)

            if self.msgWasSentOrReceived(msgRegexpBin):
                print("Starting timer")

                condTitle = condDescr['condTitle']
                toutMs = condDescr['condTimeMs']

                self.startCondTimer(condTitle, toutMs)


    def getListOfCondDescrsOfTypeTimePassedAfterSendOrReceive(self) -> list:
        listOfConditionsActivelyUsedInCurrentMode = self.getListOfCondDescrsActivelyUsedInCurrentMode()

        def condTypeIsTimePassedAfter(condDescr):
            if (condDescr['condType'] == 'condTypeTimePassedAfterStartReceivingMsg' or
                    condDescr['condType'] == 'condTypeTimePassedAfterStartSendMsg'):
                return condDescr

        listOfCondDescrs = list(filter(condTypeIsTimePassedAfter, listOfConditionsActivelyUsedInCurrentMode))

        return listOfCondDescrs


    def getAllRegexpTitlesListForCondOfTypeTimePassedAfterSendOrReceive(self) -> list:
        allCondOfTypeTimePassedAfterSendOrReceiveRegexpTitlesList = []

        listOfCondDescrsOfTypeTimePassedAfterSendOrReceive = self.getListOfCondDescrsOfTypeTimePassedAfterSendOrReceive()

        for cond in listOfCondDescrsOfTypeTimePassedAfterSendOrReceive:
            print("Processing time passed after condition...")

            allCondOfTypeTimePassedAfterSendOrReceiveRegexpTitlesList.extend(cond["condRegexpTitlesList"])

        return allCondOfTypeTimePassedAfterSendOrReceiveRegexpTitlesList


    def msgWasSentOrReceived(self, msgRegexp: str) -> bool:
        for condDescrAndReceiveFlag in self.listOfRegexpAndReceiveFlagForNotedMsgs:
            if condDescrAndReceiveFlag["regexp"] == msgRegexp and condDescrAndReceiveFlag["msgNoted"]:
                condDescrAndReceiveFlag["msgNoted"] = False
                return True
        return False


    def startTimersAfterImitStart(self) -> None:
        listOfNoneEmptyConditionsOfTypeTimePassedAfterStart = self.getListOfCondDescrsOfTypeTimePassedAfterStart()

        for condDescr in listOfNoneEmptyConditionsOfTypeTimePassedAfterStart:
            condTitle = condDescr['condTitle']
            toutMs = condDescr['condTimeMs']
            self.startCondTimer(condTitle, toutMs)


    def getListOfCondDescrsOfTypeTimePassedAfterStart(self) -> list:
        listOfConditionsActivelyUsedInCurrentMode = self.getListOfCondDescrsActivelyUsedInCurrentMode()

        def getCondTypeFunc(condDescr):
            if condDescr['condType'] == 'condTypeTimePassedAfterStart':
                return condDescr

        listOfCondDescrs = list(filter(getCondTypeFunc, listOfConditionsActivelyUsedInCurrentMode))

        return listOfCondDescrs


    def getListOfCondDescrsActivelyUsedInCurrentMode(self) -> list:
        listOfNoneEmptyConditions = self.getListOfNoneEmptyConditionsForCurrentMode()

        listOfNoneEmptyConditionTitles = [cond["condTitle"] for cond in listOfNoneEmptyConditions]

        listOfCondDescrsActivelyUsedInCurrentMode = []

        for condTitle in listOfNoneEmptyConditionTitles:
            condDescr = self.getCondDescrDictFromTitle(condTitle)
            listOfCondDescrsActivelyUsedInCurrentMode.append(condDescr)

        return listOfCondDescrsActivelyUsedInCurrentMode


    def startCondTimer(self, condTitle: str, toutMs: int) -> None:
        timer = threadTimer.ThreadTimer(self.proccessTimerTimeout, condTitle, toutMs)
        self.listOfTimers.append(timer)
        timer.start()


    @pyqtSlot(str)
    def proccessTimerTimeout(self, condTitle: str) -> None:
        listOfActionTitles = self.getListOfActionsAssignedToCondition(condTitle)

        listOfResponses = self.getListOfResponses(listOfActionTitles)

        self.signalAddListOfMsgToSendingList.emit(listOfResponses)

        self.changeModeIfNeeded(listOfActionTitles)


    def changeModeIfNeeded(self, listOfActionTitlesTriggered: list) -> None:
        for actionTitle in listOfActionTitlesTriggered:
            actionDescr = self.getActionDescrDict(actionTitle)
            actionType = actionDescr['actionType']

            if actionType == 'actionTypeChangeMode':
                newModeTitle = actionDescr['newMode']
                self.setNewAutorespMode(newModeTitle)


    def setNewAutorespMode(self, newModeTitle: str) -> None:
        print("Switching to mode", newModeTitle)
        self.currentAutorespModeTitle = newModeTitle
        self.currentAutorespModeData = self.getCurrentAutorespModeData(self.currentAutorespModeTitle)
        self.listOfRegexpAndReceiveFlagForNotedMsgs = self.getInitialListOfRegexpForNotedMsgs()


    def getListOfResponses(self, listOfActionTitlesTriggered: list) -> list:
        listOfResponses = []

        for actionTitle in listOfActionTitlesTriggered:
            listOfResponsesForAction = self.getListOfResponsesForAction(actionTitle)
            listOfResponses.extend(listOfResponsesForAction)

        return listOfResponses


    def getListOfResponsesForAction(self, actionTitle: str) -> list:
        listOfResponsesForAction = []

        actionDescr = self.getActionDescrDict(actionTitle)
        actionType = actionDescr['actionType']

        if actionType == 'actionTypeRemember' or actionType == 'actionTypeChangeMode':
            pass
        elif actionType == 'actionTypeRespondWithReceivedMsg':
            listOfResponsesForAction.append(self.msgReceived)
        elif actionType == 'actionTypeRespondWithReceivedMsgWithAssigningFields':
            args = [self.msgReceived, actionDescr['listOfFieldTitlesAndValuesToReplaceWhenRespondingWithReceivedMsg']]
            msgReceivedWithFieldsAssigned = self.assignValuesToFieldsInReceivedMsg(*args)
            listOfResponsesForAction.append(msgReceivedWithFieldsAssigned)
        elif actionType == 'actionTypeRespondWithNamedMsg' or actionType == 'actionTypeRespondWithFewNamedMsg':
            listOfResponseTitles = actionDescr["listOfMsgToRespondWith"]
            listOfResponsesForAction = list(map(self.managerNamedMsg.getHexStrByMsgTitle, listOfResponseTitles))

        return listOfResponsesForAction


    def assignValuesToFieldsInReceivedMsg(self, msg: str, listOfFieldTitlesAndValuesToAssign: list) -> str:
        msg = msg.replace(' ', '')

        for fieldTitleAndValueToAssign in listOfFieldTitlesAndValuesToAssign:
            fieldTitle = fieldTitleAndValueToAssign["fieldTitle"]

            newHexFieldValue = fieldTitleAndValueToAssign["fieldValue"]

            msg = self.msgParser.setFieldValueInMsg(msg, fieldTitle, newHexFieldValue)

        return msg


    def getActionDescrDict(self, actionTitle: str) -> dict:
        if actionTitle == 'Respond with received msg':
            actionDescr = {'actionTitle': 'Respond with received msg',
                           'actionType':  'actionTypeRespondWithReceivedMsg'}
        else:
            actionDescr = self.getActionDescrByTitle(actionTitle)

        return actionDescr


    def getActionDescrByTitle(self, actionTitle: str) -> dict:
        for action in self.actionDescrList:
            if actionTitle == action['actionTitle']:
                return action


    def getListOfActionTitlesTriggeredByReceivingMsg(self, msg) -> list:
        # TODO: Into class AutorespMode
        listOfActionsToPerform = []

        listOfConditionsForMode = self.getListOfNoneEmptyConditionsForCurrentMode()

        for condAndAssignedActions in listOfConditionsForMode:
            condTitle = condAndAssignedActions['condTitle']

            listOfActionsForCond = self.getListOfActionsToPerformForCondition(condTitle, msg)

            if len(listOfActionsForCond) > 0:
                listOfActionsToPerform.extend(listOfActionsForCond)

        return listOfActionsToPerform


    def prepareMsg(self, msg) -> str:
        if isinstance(msg, bytes):
            msg = msg.decode('utf-8', 'replace')
        msg = msg.strip('b\'')
        msg = msg.replace('\\x', "")
        msg = msg.replace('\'', '')

        return msg


    def getListOfActionsToPerformForCondition(self, condTitle: str, msg: str) -> list:
        # TODO: Into class AutorespMode
        listOfActionsToPerform = []

        stringHandler = handlerString.HandlerString()
        binMsg = stringHandler.getWholeMsgBinStrFromHexStr(msg)

        condDescr = self.getCondDescrDictFromTitle(condTitle)

        if condDescr['condType'] == 'condTypeReceivedSingleMsg':
            listOfActionsToPerform = self.getListOfActionsToPerformForCondTypeReceivedSingleMsg(condDescr, binMsg)
        elif condDescr['condType'] == 'condTypeReceivedFewMsg':
            listOfActionsToPerform = self.getListOfActionsToPerformForCondTypeReceivedFewMsg(condTitle)
        elif condDescr['condType'] == 'condTypeCompositeCond':
            listOfActionsToPerform = self.getListOfActionToPerformForCondOfTypeCompositeCond(condTitle)

        return listOfActionsToPerform


    def getListOfActionsToPerformForCondTypeReceivedSingleMsg(self, condDescr: dict,  binMsg: str) -> list:
        listOfActionsToPerform = []

        condRegexpTitlesList = condDescr["condRegexpTitlesList"]
        for regexpTitle in condRegexpTitlesList:
            msgRegexp = self.managerNamedRegexp.getBinRegexpFromRegexpTitle(regexpTitle)

            result = re.search(msgRegexp, binMsg)

            if result:
                # print("Action triggered!")
                condTitle = condDescr["condTitle"]
                listOfActionsToPerform = self.getListOfActionsAssignedToCondition(condTitle)

        return listOfActionsToPerform


    def getListOfActionsToPerformForCondTypeReceivedFewMsg(self, condTitle: str) -> list:
        listOfActionsToPerform = []

        if self.allMsgsFromConditionWereReceived(condTitle):
            listOfActionsToPerform = self.getListOfActionsAssignedToCondition(condTitle)

        return listOfActionsToPerform


    def getListOfActionToPerformForCondOfTypeCompositeCond(self, condTitle: str) -> list:
        listOfActionsToPerform = []

        condDescr = self.getCondDescrDictFromTitle(condTitle)
        condCounter = 0

        for condInCompCond in condDescr['condTitlesList']:
            condInCompCondTitle = condInCompCond['condTitle']

            if self.condHasAlreadyBeenTriggered(condInCompCondTitle):
                condCounter += 1

        if condCounter == len(condDescr['condTitlesList']):
            listOfActionsToPerform = self.getListOfActionsAssignedToCondition(condTitle)

        return listOfActionsToPerform


    def allMsgsFromConditionWereReceived(self, condTitle: str) -> bool:
        condDescr = self.getCondDescrDictFromTitle(condTitle)

        condRegexpTitlesList = condDescr["condRegexpTitlesList"]

        receivedMsgCounter = 0
        for regexpTitle in condRegexpTitlesList:
            msgRegexp = self.managerNamedRegexp.getBinRegexpFromRegexpTitle(regexpTitle)

            if self.msgWasReceived(msgRegexp):
                receivedMsgCounter += 1

        if receivedMsgCounter == len(condRegexpTitlesList):
            self.resetFactOfReceivingMsgsForCond(condTitle)
            return True
        else:
            return False


    def msgWasReceived(self, msgRegexp: str) -> bool:
        for regexpAndFlag in self.listOfRegexpAndReceiveFlagForNotedMsgs:
            if regexpAndFlag["regexp"] == msgRegexp and regexpAndFlag["msgNoted"] is True:
                return True
        return False


    def resetFactOfReceivingMsgsForCond(self, condTitle: str) -> None:
        condDescr = self.getCondDescrDictFromTitle(condTitle)

        condRegexpTitlesList = condDescr["condRegexpTitlesList"]

        regexpBinListToResetReceivedFlag = [
            self.managerNamedRegexp.getBinRegexpFromRegexpTitle(regexpTitle) for regexpTitle in condRegexpTitlesList]

        map(self.resetMsgNotedFlagIfNeeded, regexpBinListToResetReceivedFlag)


    def resetMsgNotedFlagIfNeeded(self, regexpBin: str) -> None:
        for regexpAndFlag in self.listOfRegexpAndReceiveFlagForNotedMsgs:
            if regexpAndFlag["regexp"] == regexpBin:
                regexpAndFlag["msgNoted"] = False
                break


    def proccessMsgSent(self, msgSent: str) -> None:
        # listOfConditionsWithTypeTimePassedAfterSendMsg = self.getConditionsWithTypeTimePassedAfterSendMsg()
        self.noteMsgIfNeeded(msgSent)

        self.startTimersIfNeeded()


    def getConditionsWithTypeTimePassedAfterSendMsg(self) -> list:
        listOfNoneEmptyConditions = self.getListOfNoneEmptyConditionsForCurrentMode()

        listOfNoneEmptyConditionDescrs = []
        for condition in listOfNoneEmptyConditions:
            condDescr = self.getCondDescrDictFromTitle(condition['condTitle'])
            listOfNoneEmptyConditionDescrs.append(condDescr)

        listOfCondDescrsWithTypeTimePassedAfterSendMsg = list(filter(self.condTypeIsTypeTimePassedAfterSendMsg,
                                                                     listOfNoneEmptyConditionDescrs))

        return listOfCondDescrsWithTypeTimePassedAfterSendMsg


    def getListOfNoneEmptyConditionsForCurrentMode(self) -> list:
        listOfConditions = self.currentAutorespModeData["condList"]
        listOfNoneEmptyConditions = list(filter(lambda condDescr: len(condDescr['actionsAssignedToCond']) > 0,
                                                listOfConditions))
        return listOfNoneEmptyConditions


    def condTypeIsTypeTimePassedAfterSendMsg(self, condDescr: dict) -> bool:
        if condDescr["condType"] == "condTypeTimePassedAfterSendMsg":
            return True
        else:
            return False


    def condHasAlreadyBeenTriggered(self, condTitle: str) -> bool:
        condDescr = self.getCondDescrDictFromTitle(condTitle)
        condRegexpTitlesList = condDescr["condRegexpTitlesList"]

        regexpCounter = 0
        for regexpTitle in condRegexpTitlesList:
            msgRegexp = self.managerNamedRegexp.getBinRegexpFromRegexpTitle(regexpTitle)
            if self.msgWithRegexpWasReceived(msgRegexp):
                regexpCounter += 1

        if regexpCounter == len(condRegexpTitlesList):
            return True
        else:
            return False


    def msgWithRegexpWasReceived(self, regexp: str) -> bool:
        for line in self.listOfRegexpAndReceiveFlagForNotedMsgs:
            if regexp == line["regexp"]:
                return line["msgNoted"]


    def getListOfActionsAssignedToCondition(self, condTitle: str) -> list:
        listOfActionsAssignedToCondition = []

        listOfConditionsForMode = self.currentAutorespModeData['condList']
        for condAndAssignedActions in listOfConditionsForMode:
            if condAndAssignedActions['condTitle'] == condTitle:
                listOfActionsAssignedToCondition = condAndAssignedActions["actionsAssignedToCond"]
                break

        return listOfActionsAssignedToCondition


    def getActionType(self, actionTitle: str) -> dict:
        for actionDescr in self.actionDescrList:
            if actionDescr['actionTitle'] == actionTitle:
                return actionDescr['actionType']
        return dict()


    def getCondDescrDictFromTitle(self, condTitle: str) -> dict:
        for condDescr in self.condDescrList:
            if condDescr['condTitle'] == condTitle:
                return condDescr


    def getOutgoingMsgId(self, msgTypeTitle: str) -> int:
        msgId = self.outgoingMsgId
        self.outgoingMsgId += 1

        lengthOfFieldWithRoleId = self.formatManager.getLengthOfFieldWithRoleIdInMsgType(msgTypeTitle)

        valueMax = pow(2, lengthOfFieldWithRoleId)
        if msgId == valueMax:
            msgId = 0
            self.outgoingMsgId = 1

        return msgId


    def setIdInOutgoingMsg(self, msg: str) -> str:
        msgTypeDict = self.msgParser.getMsgDictFromMsg(msg)

        if msgTypeDict["msgTypeTitle"] == "undef" or \
           msgTypeDict["isReceipt"]:
            return msg

        msgTypeTitle = self.msgParser.getMsgTypeFromMsg(msg)
        idForMsg = self.getOutgoingMsgId(msgTypeTitle)

        idHandler = handlerId.HandlerId(self.profileTitle)
        msg = idHandler.setIdInMsg(msg, str(idForMsg))

        return msg
