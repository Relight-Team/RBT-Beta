# This class will allow both command arguments and config file in the form of a class, allows us to interact with configs much easier
class Build_Config:

    # If true, then any Archive that is outdated will be ignored
    # Can be overwritten with: Config File
    IgnoreOutdatedArchive = True

    # If true, then when building engine modules, we use already compiled libraries instead of new ones
    # Can be overwritten with: Command Line
    Precompiled = False

    # If true, then we will parallel executor if available
    # Can be overwritten with: Config File
    TryParallelExecutor = True

    # If true, we will use the Header Tool, otherwise, we will skip it
    UseHeaderTool = False  # TODO: Change to true once we implement header tool
