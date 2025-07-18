from colorama import Fore, Back, Style
import inspect
import os


# Logger system, will print out debugging info based on level
#
# Levels:
# 1 - logs detailed info like return statements and important if statement calls
# 2 - logs additional info that tracks content like what file we are writing and important OS operations
# 3 - logs basic info of what stage of process we are on
# 4 - Warns if there's issue, will continue running (cannot be disabled)
# 5 - Fatal error, will close the program (cannot be disabled)
def Logger(Level, Str):
    # FIXME: This is all temp since I'm lazy and don't want to implement the config system, pls add config system. Also add writing file log support

    Ret = ""

    Color = Style.RESET_ALL

    LogType = "[LOG]"

    FileName = "FileNone, if you see this message then something def fucked up"
    ClassName = "ClassNone"
    FuncName = "FuncNone"

    # Set values of filename, class name, and function function name

    # SHITTY HACK ALERT! SHITTY HACK ALERT!
    # After many research of videos, stackoverflow, and the shitty ChatGPT shit, I think I can put together a way to finaly make this frankenstein code work so that we can return info on the function

    # -- Get's File Name -- #

    Frame = inspect.currentframe()  # Idk what the fuck this does but it's important
    Caller = Frame.f_back  # Get's the current file
    Filepath = Caller.f_code.co_filename  # Get's full file path
    Name = os.path.basename(Filepath)  # just get file name

    if Name != None and Name != "":
        FileName = Name

    # -- Get's Function Name -- #

    Func = Caller.f_code.co_name  # This fun little code get's the function name

    if Func != "<module>":
        FuncName = Func

    # -- Get's Class Name -- #

    # If you are wondering what exactly is happening in this code, join the club, idk stack overflow and AI told me to do this, please add good documentation later
    Stack = inspect.stack()
    # The caller's frame is at index 1 in the stack
    Callerframe = Stack[1]
    if "self" in Callerframe.frame.f_locals:
        CallerInstance = Callerframe.frame.f_locals["self"]
        ClassName = CallerInstance.__class__.__name__

    # Ok now we are done with that we can add all this to our log

    Ret = "{" + FileName + "}{" + ClassName + "}{" + FuncName + "} "

    # Get Color info and label

    if Level == 4:
        Ret += Fore.YELLOW + "[WARNING] "
    elif Level == 5:
        Ret += Fore.RED + "[FATAL] "
    else:
        Ret += "[LOG: " + str(Level) + "] "

    Ret += Str + Style.RESET_ALL

    print(Ret)

    if Level == 5:
        raise ValueError("Encountered fatal error, exiting...")
