import os
import sys
from enum import Enum

sys.path.append("../")

import Internal.Core as C

class Target:

    # The name of the target, will be used as the executable name (unless project file overrides it)
    Name = "Relight_Program"

    # The target type, can be either Game, Editior, Client, Server, or Program
    TargetType = "Game"

    # The Build type, determines what debugging tools we should include, can be either Debug, Development, and Final
    BuildType = "Development"

    # All additional dependencies for the target to compile
    ExtraDependencies = []

    # If true, will not create any debug related files
    DisableDebugInfo = False


    # -- Internal variables -- #

    InternalTargetDirectory = ""

    def __init__(TargetFile):

        # Set public variables

        Name = C.GetVar(TargetFile, "Name")
        TargetType = C.GetVar(TargetFile, "TargetType")
        ExtraDependencies = C.GetVar(TargetFile, "ExtraDependencies")

        # Set private variables

        InternalTargetDirectory = os.path.dirname(TargetFile)
