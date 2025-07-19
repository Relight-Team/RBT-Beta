import os
import sys

sys.path.append("../")

import Internal.Core as C


class BuildModule:

    # The name of the module
    Name = ""

    # The name of the object, mainly should be used for long module names
    ObjectName = Name

    # The description of the module, mainly used for documentation and debugging
    Description = ""

    # The type of module, can either be Internal or External (Internal: Relight-based project. External: 3rd-party project)
    Type = ""

    # The list of dependencies this module requires
    Modules = []

    # Names of Modules we will include
    ModulesIncludes = []

    # All directories we will include
    Includes = []

    SysIncludes = []

    # Defines for this specific module
    Defines = []

    # Directories to search for dynamic libraries
    DynamicModulePaths = []

    # Static libraries for 3rd parties
    Static3rdParty = []

    # Third party, will be added to Static3rdParty and Includes
    ThirdParty = []

    # What level of optimization we should use, less optimization = faster compiling and debugging, but bigger file size
    Optimization = "Default"

    # If true, we will not use UNITY system on this module, even if the target/project file allows UNITY
    DisableUnity = False

    # if we should use RTTI (run time type information)
    RTTI = False

    # if we should use AVX instructions
    AVX = False

    # If true, then we will automatically append Includes to have Modules, you will have to manually do it if false
    AutoIncludeModules = True

    # If true, we will treat it as a engine module (put module in engine dir instead of project dir)
    IsEngineModule = False

    # -- Read Only -- #

    # The entire file path (Dir1/Dir2/Example.Module)
    FilePath = ""

    # The directory to the file (Dir1/Dir2/)
    ModuleDirectory = ""

    def __init__(BuildFile):

        FilePath = BuildFile

        ModuleDirectory = os.path.dirname(FilePath)

        # Set public variables

        Name = C.GetVar(BuildFile, "Name")
        Name = C.GetVar(BuildFile, "ObjectName")
        Description = C.GetVar(BuildFile, "Description")
        Modules = C.GetVar(BuildFile, "Modules")
        ThirdPartyDependencies = C.GetVar(BuildFile, "ThirdPartyDependencies")
