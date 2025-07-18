from enum import Enum
import sys

from Internal import ActionListManager
from Internal import TargetBuilder
from Internal import ActionListManager

from Template import Platform

from Readers import TargetReader

class Options(Enum):

    SkipBuild = False # If we should skip the build, used for testing

    NoMessages = False # If true, do not print anything

    Precompile = False # If true, we will use precompiled binary for engine modules


# The main function we are going to execute in this mode
def Main(Args):

    # Convert Args to StartingTarget

    StartingTarget = TargetReader.StartingTarget(Args.GetAndParse("Platform"))

    #TODO: Add Project Reader support to read targets listed in that, for now we will always use -Target= argument

    StartingTarget.Name = Args.GetAndParse("Target")

    StartingTarget.Project = Args.GetAndParse("Project")

    StartingTarget.Modules = Args.GetAndParse("Module")

    print("Building " + str(StartingTarget.Name))

    StartingTargetList = []
    StartingTargetList.append(StartingTarget)

    BuildProcess(StartingTargetList, Options, None, Options)


# Build's the list of target
def BuildProcess(StartingTargetList, BuildConfig, WorkingSet, InOptions):

    if InOptions.SkipBuild == False:

        ExecuteActionsTarget = []

        # Have a list to convert all targets into actions
        for Item in StartingTargetList:
            FileBuild = CreateAndRunTargetBuilder(BuildConfig, Item, WorkingSet)
            TargetAction = GetActionFromTarget(Item, BuildConfig, FileBuild)
            ExecuteActionsTarget.append(TargetAction)

        # If there's only one target, add it to the action to execute, otherwise we will combine them into one list of actions
        if len(StartingTargetList) == 1:
            ExecuteActions = []
            ExecuteActions.append(ExecuteActionsTarget[0])
        else:
            ExecuteActions = MergeActionList(StartingTargetList, ExecuteActionsTarget)

        # Link actions together
        ActionListManager.Link(ExecuteActions)

        # Ensures that each item has the same config
        for Item in StartingTargetList:
            BuildPlatform = Platform.Platform.GetBuildPlatform(Item.Platform)
            # TODO: Sync XGE, Distcc, and SNDBS from BuildPlatform to BuildConfig, should only be set true/false if all of them are that value

        if len(ExecuteActions) == 0 and InOptions.NoMessages == True:
            print("All targets are up to date") # TODO: replace this with log class

        else:
            # Execute Actions
            ActionListManager.Execute(BuildConfig, ExecuteActions)


# Create's a TargetBuilder and build's it
def CreateAndRunTargetBuilder(BuildConfig, StartingTarget, WorkingSet):

    Builder = TargetBuilder.TargetBuilder.Create(StartingTarget) # This will create TargetRules as well

    return Builder.Build(BuildConfig, WorkingSet, True)


# Create's a Relight Header file
def CreateRHFile():
    pass


# if there's multiple target's, we will merge them together into a single action list and return the new list
def MergeActionList(TargetList, ActionList):
    pass


# Get all actions to execute
def GetActionFromTarget(StartingTarget, BuildConfig, FileBuild):

    ActionListManager.Link(FileBuild.ActionList) # Link the main action list

    #TODO: Add Hot Reload support

    PreconditionActions = GetPreconditionActions(StartingTarget, FileBuild)

    ActionListManager.Link(PreconditionActions) # Link the precondition action list

    #TODO: add CppDependencies support

    ActionsToExecute = ActionListManager.GetActionToExecute(FileBuild.ActionList, PreconditionActions, None, None, False) # TODO: This is a temp

    return ActionsToExecute



# This will get all precondition from actions
def GetPreconditionActions(StartingTarget, FileBuild):
    Ret = []

    #TODO: Add SingleFileToCompile support!

    Ret = GetPreconditionActionsFromActions(FileBuild.ActionList, Ret)

    return Ret


# Function that helps GetPreconditionActions
def GetPreconditionActionsFromActions(ActionList, OutputList):
    Ret = []

    for Action in ActionList:
        GetPreconditionActionsFromSingleAction(Action, OutputList)


# Function that helps GetPreconditionActions
def GetPreconditionActionsFromSingleAction(Action, OutputList):
    if any(Output in OutputList for Output in Action.OutputItems):
        if not Action in OutputList:
            OutputList.add(Action)

            for Precondition in Action.PreconditionActions:
                GetPreconditionActionsFromSingleAction(Precondition, OutputList)
