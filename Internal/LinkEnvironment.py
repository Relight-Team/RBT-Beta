import CompileEnvironment as CE

class LinkEnvironment:

    Platform = CE.Platform

    Config = CE.Config

    Arch = ""

    BundleDir = ""

    OutputDir = ""

    IntermediateDir = ""

    LocalShadowDir = ""

    OutputPaths = []

    LibraryPaths = []

    ExcludeLibs = []

    AdditionalLibs = []

    RuntimeLibPaths = []

    AdditionalFrameworks = []

    AdditionalBundlesRes = []

    DelayLoadDynamics = []

    AdditionalArgs = ""

    AddDebugInfo = True

    DisableSymbolCashe = False

    IsBuildingLibrary = False

    IsBuildingDynamic = False

    IsTerminalSoftware = False

    DefaultStackSize = 5000000

    OptimizeSize = False

    ExcludeFramePointers = True

    IncrementalLinking = False

    AllowLTCG = False

    PGOProfile = False

    PGOOptimize = False

    PGODirectory = ""

    PGOFilePrefix = ""

    CreateMapFile = False

    AllowASLR = False

    UseFastPDBLinking = False

    PrintTimingInfo = False

    InputFiles = []

    InputLibs = []

    DefaultResFiles = []

    GlobalResFiles = []

    IncFunctions = []

    DefineFiles = []

    AdditionalProperty = []

    def __init__(self, InPlatform, InConfig, InArch):
        self.Platform = InPlatform
        self.Config = InConfig
        self.Arch = InArch

    def __init__(self, Second):
        self.Platform = Second.Platform
        self.Config = Second.Config
        self.Arch = Second.Arch
        self.BundleDir = Second.BundleDir
        self.OutputDir = Second.OutputDir
        self.IntermediateDir = Second.IntermediateDir
        self.LocalShadowDir = Second.LocalShadowDir
        self.OutputPaths = self.OutputPaths + Second.OutputPaths
        self.LibraryPaths = self.LibraryPaths + Second.LibraryPaths
        self.ExcludeLibs = self.ExcludeLibs + Second.ExcludeLibs
        self.AdditionalLibs = self.AdditionalLibs + Second.AdditionalLibs
        self.RuntimeLibPaths = self.RuntimeLibPaths + Second.RuntimeLibPaths
        self.AdditionalFrameworks = self.AdditionalFrameworks + Second.AdditionalFrameworks
        self.AdditionalBundlesRes = self.AdditionalBundlesRes + Second.AdditionalBundlesRes
        self.DelayLoadDynamics = self.DelayLoadDynamics + Second.DelayLoadDynamics
        self.AdditionalArgs = Second.AdditionalArgs
        self.AddDebugInfo = Second.AddDebugInfo
        self.DisableSymbolCashe = Second.DisableSymbolCashe
        self.IsBuildingLibrary = Second.IsBuildingLibrary
        self.IsBuildingDynamic = Second.IsBuildingDynamic
        self.IsTerminalSoftware = Second.IsTerminalSoftware
        self.DefaultStackSize = Second.DefaultStackSize
        self.OptimizeSize = Second.OptimizeSize
        self.ExcludeFramePointers = Second.ExcludeFramePointers
        self.IncrementalLinking = Second.IncrementalLinking
        self.AllowLTCG = Second.AllowLTCG
        self.PGOProfile = Second.PGOProfile
        self.PGOOptimize = Second.PGOOptimize
        self.PGODirectory = Second.PGODirectory
        self.PGOFilePrefix = Second.PGOFilePrefix
        self.CreateMapFile = Second.CreateMapFile
        self.AllowASLR = Second.AllowASLR
        self.UseFastPDBLinking = Second.UseFastPDBLinking
        self.PrintTimingInfo = Second.PrintTimingInfo
        self.InputFiles = self.InputFiles + Second.InputFiles
        self.InputLibs = self.InputLibs + Second.InputLibs
        self.DefaultResFiles = self.DefaultResFiles + Second.DefaultResFiles
        self.GlobalResFiles = self.GlobalResFiles + Second.GlobalResFiles
        self.IncFunctions = self.IncFunctions + Second.IncFunctions
        self.DefineFiles = self.DefineFiles + Second.DefineFiles
        self.AdditionalProperty = self.AdditionalProperty + Second.AdditionalProperty

    def OutputFilePath():
        if len(OutputPaths) == 1:
            return OutputPaths[0]
        else:
            raise ValueError("OutputPaths must only have 1 item when attempting to run LinkEnvironment.OutputFilePaths(), the count we detected is " + str(len(OutputPaths)))
