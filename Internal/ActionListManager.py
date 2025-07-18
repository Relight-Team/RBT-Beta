from . import Action
from . import ActionExecute
from . import Logger

from functools import cmp_to_key



# Sort the list (this is to help executer)
def Sort(ActionList):

    # Reset all DependCount
    for Item in ActionList:
        Item.DependCount = 0

    # Set all DependCount

    for Item in ActionList:
        Lis = []
        Item.AddDependCount(Lis)

    # We can now sort ActionList

    Ret = ActionList.sort(key=cmp_to_key(Action.Action.ComparePrecondition))

    ActionList = Ret


# Checks if there's a circular dependency (when modules rely on each other)
def CycleDetection(ActionList, ItemActionDictionary):
    pass


# Add's the PreconditionListOutput of all actions and it's Precondition
def GetPrecondition(ActionList, PreconditionListOutput):

    # For each action, run the GetPreconditionSingle

    for Item in ActionList:
        GetPreconditionSingle(Item, PreconditionListOutput)


# Add's the PreconditionListOutput of an action and all it's Precondition
def GetPreconditionSingle(InAction, PreconditionListOutput):

    # Ensure's that there are no duplicates
    if not InAction in PreconditionListOutput:
        PreconditionListOutput.append(InAction) # Add self to list

        # Adds all Precondition Items to list, via recursive
        for Item in InAction.PreconditionActions:
            GetPreconditionSingle(Item, PreconditionListOutput)


# Checks if there's any issues with the action list
def CheckConflicts(ActionList):
    pass


# Get's all Actions that are oudated
def GetAllOutdatedActions(ActionList, History, OutdatedActionList, DependCashe, IgnoreOutdatedLib):
    pass


# Deletes all files that are outdated
def DeleteOutdatedFiles(OutdatedActionList):
    pass

# Link the actions together
def Link(ActionList):

    # This dictionary will attach each output file to an action, there can be multiple actions per file, but only one file name
    # Example:
    # File1.o | Action1
    # File2.a | Action1
    # Output.exe | Action2
    ItemAction = {}

    for Item in ActionList:

        for Fil in Item.OutputItems:
            ItemAction[Fil] = Item

    # Checks for any cycles
    CycleDetection(ActionList, ItemAction)

    # Set the PreconditionAction for each action
    for Item in ActionList:
        # Clear PreconditionAction in the action
        Item.PreconditionAction = []

        # For each PreconditionItems, add it the action's PreconditionActions if it's not in ItemAction list
        for PreItem in Item.PreconditionItems:

            if not PreItem in ItemAction:
                New = ItemAction[PreItem]
                Item.PreconditionActions.append(New)


    # Sorts the action list
    Sort(ActionList)


# Returns all Actions to Execute
def GetActionToExecute(ActionList, PreconditionActionList, CppCache, IgnoreOutdatedLib, History=None):

    ActionOutdatedMap = {} # Action | Bool

    # By default, set everything to true
    for Item in PreconditionActionList:
        ActionOutdatedMap[Action] = True

    ActionOutdatedDict = {} # Action | Bool

    GetAllOutdatedActions(ActionList, History, ActionOutdatedDict, CppCashe, IgnoreOutdatedLib)

    Ret = []

    # Set Ret to all actions to execute, so long as it's not invalid or outdated
    for Item in ActionList:
        if Item.CommandPath != None and Item in ActionOutdatedMap:
            if ActionOutdatedDict[Item] == True:
                Ret.append(Item)

    return Ret


# Execute the list of actions
def Execute(BuildConfig, ActionToExecuteList):

    # If the list is empty, we can quit the execution
    if len(ActionToExecuteList) == 0:
        return

    Executer = ActionExecute.LinearExecuter # FIXME: As a temp solution, we are just using LinearExecuter, add support for switching to multiple executers!

    # Execute the action list, stores if successful
    Ex = Executer.ExecuteActionList(ActionToExecuteList)

    # If not successful, throw an error

    if Ex == False:
        raise ValueError("We have failed to run ActionToExecuteList") # TODO: Add detailed description

    # FIXME: Verify and read all file output info

