import subprocess
import threading
import os

# This handles the different types of execution of the list of actions

class Thread:

    ExitCode = 0

    Action = None

    Finished = False

    def __init__(self, InAction):
        Action = InAction

    # These 2 functions will allow the program to print the output that should be printed from the command line
    def _ReadOutput(self, pipe):
        for line in iter(pipe.readline, b''):
            print(f"{line.decode().strip()}")
        pipe.close()

    def _ReadError(self, pipe):
        for line in iter(pipe.readline, b''):
            print(f"{line.decode().strip()}")
        pipe.close()

    # The function that will be run by the thread, this will execute the process based on the action
    def FunctionToRun(self):
        print("Executing " + str(self.Action.CommandPath)  + " " + str(self.Action.Arguments))

        # Start program
        try:
            try:
                args = [self.Action.CommandPath, self.Action.Arguments] # Combines file path and arguments
                RunningProgram = subprocess.Popen(args, cwd=self.Action.CurrentDirectory, stdout=self.subprocess.PIPE, stderr=self.subprocess.PIPE, text=True)

                # Run ReadOutput and ReadError

                self._ReadOutput(RunningProgram.stdout)
                self._ReadError(RunningProgram.stderr)
            except:
                pass

            process.wait() # Wait until program stops running

            self.ExitCode = Process.returncode

        except:
            pass

        self.Finished = True



    # Starts the threading
    def Start(self):
        thread = threading.Thread(target=self.FunctionToRun)
        thread.start()

class ExecuteBase:

    def Name():
        return "Base"

    def ExecuteActionList(ActionList):
        pass # Overritten by child class

# Executes actions one at a time
class LinearExecuter(ExecuteBase):

    def Name():
        return "Linear"

    def ExecuteActionList(ActionList):

        ActionThreadDict = {} # A dictionary of Action : Thread

        print("Compiling C++ Code...")

        Progress = 0

        Loop = True

        # Loop until we are done
        while(Loop):

            ExeAction = 0 # All actions that we are currently executing
            NonExeAction = 0 # All actions that isn't executed

            # we will update ExeAction and NonExeAction every loop instance
            for i in ActionList:
                InpThread = None

                # if the action key is not in the dictionary, add 1 to NonExeAction
                if not i in ActionThreadDict:
                    NonExeAction += 1

                # else, if the thread (value of key) is not None but the thread is not finished, add 1 to both ExeAction and NonExeAction
                else:
                    InpThread = ActionThreadDict[i]
                    if InpThread is not None and InpThread.Finished == False:
                        ExeAction += 1
                        NonExeAction += 1

            # Update the progress
            Progress = len(Actions) + 1 - NonExeAction

            # If we have no more actions that isn't executed, then we can stop
            if NonExeAction == 0:
                Loop = False


            for i in ActionList:

                ActionThr = None

                ActionThrFound = False

                # if true, set both ActionThrFound and ActionThr
                if i in ActionThreadDict:
                    ActionThrFound = True
                    ActionThr = ActionThreadDict[i]

                if ActionThrFound == False:

                    # if Execute Actions is less than the cpu count
                    if ExeAction < max(1, os.cpu_count()):
                        ContainOutdatedPre = False # If any action's Precondition is outdated
                        ContainFailedPre = False # If any action's Precondition has failed

                        # Detect if any Precondition Actions is either outdated or has failed
                        for j in self.Action.PreconditionActions:

                            # Detect if any Precondition Actions is either outdated or has failed
                            if j in ActionThreadDict:
                                PreThread = ActionThreadDict[j]

                                if PreThread == None:
                                    ContainFailedPre = True

                                elif PreThread.Finished == False:
                                    ContainOutdatedPre = True

                                elif PreThread.ExitCode != 0:
                                    ContainFailedPre = True
                            else:
                                ContainOutdatedPre = True

                        # If we failed, we can add the action to dictionary, but we should leave the thread blank, since we are not ready to execute yet
                        if ContainFailedPre == True:
                            ActionThreadDict[i] = None

                        # If it hasn't failed and isn't outdated, add action and the thread to the dictionary
                        elif ContainFailedPre == False:

                            TD = Thread(i) # Store action to execute
                            try:
                                TD.Start() # Execute action

                            except:
                                pass

                            ActionThreadDict[i] = TD # Store Action with the value of the thread into the dictoonary

                            ExeAction += 1 # add 1 to Executing Actions


        Ret = True

        # If there's any errors in the dictionary, return false
        for Action, Thread in ActionThreadDict:

            if thread == None or thread.ExitCode != 0:
                Ret = False

        # Return's the Ret value, this will let us know if there was any errors (true if no errors, false if there was errors)
        return Ret




# TODO: Add support for ParallelExecuter
# Executes multiple actions at a time
#class ParallelExecuter(ExecuteBase)
