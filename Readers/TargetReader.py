import os
import sys
from enum import Enum

sys.path.append("../")

import Internal.Core as C

# Stores target-specific arguments from the command line/Config File, will overwrite any default settings
class StartingTarget:
    pass


# The main target class, stores everything store in .target file
class Target:

    # The name of the target, will be used as the executable name (unless project file or command argument overrides it). If blank or none, we will use the target file name instead
    Name = None

    # The target type, can be either Game, Editior, Client, Server, or Program. Used for enabiling some settings
    TargetType = "Game"

    # The Build type, determines what debugging tools we should include, can be either Debug, Development, and Final
    BuildType = "Development"

    # The type of link, if it’s Monolithic, it’s all in the same executable, if it’s Modular, then each module is a dynamic library alongside the executable
    LinkType = "Default"

    # The intermediate type, Shared for Engine in engine intermediate, Unique for Everything in project intermediate
    IntermediateType = "Default"

    # All additional dependencies for the target to compile
    ExtraDependencies = []

    # If true, will not create any debug related files
    DisableDebugInfo = False

    # If true, then instead of compiling this target as an executable, we compile it as a library
    IsDynamicLibrary = False

    # If true, we will compile the editor, otherwise we do not need to compile the editor
    CompileEditor = False

    # If true, we will use existing Engine static libraries via intermediate directories instead of compiling the engine each time
    UseCompiledEngine = False

    # If true, we will use the UNITY system, which will combine all C++ in a module into a singular file
    Unity = True

    # Defines that will be spread throughout every module
    Defines = []

    # If true, then we will include the module that launches the application
    IncludeLaunch = True

    # If IncludeLaunch is true, then we will search for the name of the launcher
    LaunchName = "Launch"

    # Any additional arguments to pass when compiling
    ExtraCompileArgs = []

    # Any additional arguments to pass when Linking
    ExtraLinkingArgs = []

    # The file of the target
    _File = None

    # The project file if it exists
    _Project = None


    def __init__(self, TargetFile, Args, ProjectFile=None):

        # Set public variables

        Name = C.GetVar(TargetFile, "Name")
        TargetType = C.GetVar(TargetFile, "TargetType")
        ExtraDependencies = C.GetVar(TargetFile, "ExtraDependencies")
