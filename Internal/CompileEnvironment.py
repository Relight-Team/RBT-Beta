class Platform:
    Unix = 0
    Windows = 1

class Config:
    Debug = 0
    Dev = 1
    Final = 2

class PCHAction:
    Null = 0
    Include = 1
    Create = 2

class Output:
    ObjectFiles = []
    DebugFiles = []
    PCHFile = ""

class CompileEnvironment:

    Plat = Platform

    Conf = Config

    PCH_Act = PCHAction.Null

    Out = Output

    Arch = ""

    SharedPCH = []

    PCHIncludeName = ""

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

    Defines = []

    AdditionalArgs = ""

    AdditionalFrameworks = []

    PCHFile = ""

    UsingRHT = False

    DefaultHideSymbols = False

    def __init__(self, InPlatform, InConfig, InArch):
        self.Plat = InPlatform

        self.Conf = InConfig

        self.Arch = InArch

        self.SharedPCH = []

        self.UserIncPaths = []

        self.SysIncPaths - []


    def __init__(self, Second):
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
        self.DefaultHideSymbols = Second.DefaultHideSymbols
