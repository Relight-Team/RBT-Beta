from enum import Enum
import sys

sys.path.append("../Internal")

import ActionListManager

sys.path.append("../Template")

import Platform

class Options(Enum):

    SkipBuild = False # If we should skip the build, used for testing

    NoMessages = False # If true, do not print anything


def Main(Args):
    pass


def BuildProcess(TargetList, BuildConfig, WorkingSet, InOptions):

    if InOptions.SkipBuild == False:

        ExecuteActionsTarget = []

        # Have a list ot convert all targets into actions
        for Item in TargetList:
            Temp = GetActionFromTarget(Item, BuildConfig)
            ExecuteActionsTarget.append(Temp)

        # If there's only one target, add it to the action to execute, otherwise we will combine them into one list of actions
        if len(TargetList) == 1:
            ExecuteActions = []
            ExecuteActions.append(ExecuteActionsTarget[0])
        else:
            ExecuteActions = MergeActionList(TargetList, ExecuteActionsTarget)

        # Link actions together
        ActionListManager.Link(ExecuteActions)

        # Ensures that each item has the same config
        for Item in TargetList:
            BuildPlatform = Platform.Platform.GetBuildPlatform(Item.Platform)
            # TODO: Sync XGE, Distcc, and SNDBS from BuildPlatform to BuildConfig, should only be set true/false if all of them are that value

        if len(ExecuteActions) == 0 and InOptions.NoMessages == True:
            print("All targets are up to date") # TODO: replace this with log class

        else:
            # Execute Actions
            ActionListManager.Execute(BuildConfig, ExecuteActions)




def CreateUHTFile():
    pass

# if there's multiple target's, we will merge them together into a single action list and return the new list
def MergeActionList(TargetList, ActionList):
    pass


def GetActionFromTarget(Target, BuildConfig):
    pass
