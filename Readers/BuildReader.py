import os
import sys

sys.path.append("../")

import Internal.Core as C

class BuildModule:

    # The name of the module
    Name = ""

    # The description of the module, mainly used for documentation and debugging
    Description = ""

    # The list of dependencies this module requires
    Dependencies = []

    # The list of third party dependencies this module requires
    ThirdPartyDependencies = []

    # -- Internal variables -- #

    # The full directory that contains the build file
    InternalBuildDirectory = ""

    def __init__(BuildFile):

        # Set public variables

        Name = C.GetVar(BuildFile, "Name")
        Description = C.GetVar(BuildFile, "Description")
        Dependencies = C.GetVar(BuildFile, "Dependencies")
        ThirdPartyDependencies = C.GetVar(BuildFile, "ThirdPartyDependencies")

        # Set private variables

        InternalBuildDirectory = os.path.dirname(BuildFile)
