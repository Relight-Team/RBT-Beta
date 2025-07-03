from enum import Enum

class Platform(Enum):
    Linux = 0
    Windows = 1

class Config(Enum):
    Debug = 0
    Dev = 1
    Final = 2

class PCHAction(Enum):
    Null = 0
    Include = 1
    Create = 2

class Output:
    ObjectFiles = []
    DebugFiles = []
    PCHFile = ""

# Configuration to compile source files into oject files
class CompileEnvironment:

    Plat = Platform # The platform we are compiling

    Conf = Config # What debugging mode we will use

    PCH_Act = PCHAction.Null # The action we will use for PCH files

    Out = Output # All output info

    Arch = "" # The CPU architecture

    SharedPCH = [] # The Header file we will use globally

    PCHIncludeName = "" # The name of the header file we will precompile

    UseSharedBuildEnv = False

    UseAVX = False

    UseRTTI = False

    UseInlining = False

    BufferSecurityChecks = True

    FalseUnityOverride = False # Use if it's faster to not use UNITY system, will disable UNITY even if it's on

    MinUnitySource = 0

    MinPCHSource = 0

    BuildLocallySNDBS = False

    ExceptionHandling = False

    ShadowVariableWarnings = True

    ShadowVariableAsError = False

    UndefinedIdentifierWarnings = True

    UndefinedIdentifierAsError = False

    Optimize = False

    OptimizeSize = False

    AddDebugInfo = True

    IsLibrary = False

    IsDynamic = False

    UseStaticCRT = False

    UseDebugCRT = False

    ExcludeFramePointers = True

    incrementalLinking = True

    AllowLTCG = False

    PGOProfile = False

    PGOOptimize = False

    PGODirectory = ""

    PGOFilePrefix = ""

    PrintTimingInfo = False

    GenerateDependFile = True

    AllowRemotelyCompiledPCHs = False

    UserIncPaths = []

    SysIncPaths = []

    CheckSysHeaderForChanges = False

    ForceIncFiles = []

    Defines = [] # Definitions we will use across the engine

    AdditionalArgs = "" # Any additional arguments we will use

    AdditionalFrameworks = []

    PCHFile = ""

    UsingRHT = False

    HideSymbols = False

    def __init__(self, InPlatform, InConfig, InArch):
        self.Plat = InPlatform

        self.Conf = InConfig

        self.Arch = InArch

        self.SharedPCH = []

        self.UserIncPaths = []

        self.SysIncPaths = []


    def Dup(self, Second):
        self.Plat = Second.Plat
        self.Conf = Second.Conf
        self.PCH_Act = Second.PCH_Act
        self.Out = Second.Out
        self.Arch = Second.Arch
        self.SharedPCH = Second.SharedPCH
        self.PCHIncludeName = Second.PCHIncludeName
        self.UseSharedBuildEnv = Second.UseSharedBuildEnv
        self.UseAVX = Second.UseAVX
        self.UseRTTI = Second.UseRTTI
        self.UseInlining = Second.UseInlining
        self.BufferSecurityChecks = Second.BufferSecurityChecks
        self.FalseUnityOverride = Second.FalseUnityOverride
        self.MinUnitySource = Second.MinUnitySource
        self.MinPCHSource = Second.MinPCHSource
        self.BuildLocallySNDBS = Second.BuildLocallySNDBS
        self.ExceptionHandling = Second.ExceptionHandling
        self.ShadowVariableWarnings = Second.ShadowVariableWarnings
        self.ShadowVariableAsError = Second.ShadowVariableAsError
        self.UndefinedIdentifierWarnings = Second.UndefinedIdentifierWarnings
        self.UndefinedIdentifierAsError = Second.UndefinedIdentifierAsError
        self.Optimize = Second.Optimize
        self.OptimizeSize = Second.OptimizeSize
        self.AddDebugInfo = Second.AddDebugInfo
        self.IsLibrary = Second.IsLibrary
        self.IsDynamic = Second.IsDynamic
        self.UseStaticCRT = Second.UseStaticCRT
        self.UseDebugCRT = Second.UseDebugCRT
        self.ExcludeFramePointers = Second.ExcludeFramePointers
        self.incrementalLinking = Second.incrementalLinking
        self.AllowLTCG = Second.AllowLTCG
        self.PGOProfile = Second.PGOProfile
        self.PGOOptimize = Second.PGOOptimize
        self.PGODirectory = Second.PGODirectory
        self.PGOFilePrefix = Second.PGOFilePrefix
        self.PrintTimingInfo = Second.PrintTimingInfo
        self.GenerateDependFile = Second.GenerateDependFile
        self.AllowRemotelyCompiledPCHs = Second.AllowRemotelyCompiledPCHs
        self.UserIncPaths = Second.UserIncPaths
        self.SysIncPaths = Second.SysIncPaths
        self.CheckSysHeaderForChanges = Second.CheckSysHeaderForChanges
        self.ForceIncFiles = self.ForceIncFiles + Second.ForceIncFiles
        self.Defines = self.Defines + Second.Defines
        self.AdditionalArgs = Second.AdditionalArgs
        self.AdditionalFrameworks = self.AdditionalArgs + Second.AdditionalArgs
        self.PCHFile = Second.PCHFile
        self.UsingRHT = Second.UsingRHT
        self.HideSymbols = Second.DefaultHideSymbols
