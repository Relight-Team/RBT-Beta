import os
import ModuleBuilder
import Binary

sys.path.append("../Readers")

import ModuleReader

sys.path.append("../Template")

import Platform

# Builds a target, will use ModuleBuilder
class TargetBuilder:

    Target = None # The TargetReader class

    PlatformIntermed = None # Intermediate directory for the platform

    PlatformIntermedFolder = None #

    EngineIntermed = None # Intermediate directory for engine binary

    ProjectDir = None # The project directory, if doesn't exist, we will use engine directory instead

    Binaries = []

    ModuleName_ModuleBuilder = {}

    def __init__(StartingTarget, InTarget):
        Target = InTarget

        PlatformIntermedFolder = GetIntermediateProject(Target._Platform, Target.Arch)

        # Overwrite target file with starting target properties
        if StartingTarget.Modules != [] and StartingTarget.Modules != None:
            Target.Modules = StartingTarget.Modules

        if Target._Project != None and Target._Project != "":
            ProjectDir = os.path.dirname(Target._Project)
        else:
            ProjectDir = ENGINEDIR #FIXME: REPLACE THIS WITH ACTUAL ENGINE DIR VAR

        PlatformIntermed = os.path.join(ProjectDir, PlatformIntermedFolder, Target.Name, Target.BuildType)

        if Target.IntermediateType == "Unique":
            EngineIntermed = PlatformIntermed

        else:
            EngineIntermed = os.path.join(ENGINEDIR, PlatformIntermed, Target.Name, Target.BuildType)



    @staticmethod
    def GetIntermediateProject(Platform, Arch):
        return os.path.join("Intermediate", "Build", Platform, Arch)


    def GetModuleOutputDir(Module):
        Ret = ""

        if Module.IsEngineModule == False or Target.IntermediateType == "Unique":
            Ret = os.path.basedir(Target._Project)
        else:
            Ret = ENGINEDIR

        return Ret


    def GetIntermediateModule(Module):
        Base = GetModuleOutputDir(Module)

        IntermedTemp = os.path.join(Base, PlatformIntermed, Target.Name, Target.BuildType)

        if Module.ObjectName != None and Module.ObjectName != "":
            Temp = Module.ObjectName
        else:
            Temp = Module.Name

        return os.path.join(IntermedTemp, Temp)


    def CreateToolchain(Platform):

        if Target.ToolchainOverride == None:
            PlatformClassTemp = Platform.GetBuildPlatform(Platform)

            return PlatformClassTemp.CreateToolChain(Platform, Target)

        else:

            pass # FIXME: Add support for ToolchainOverride



    def GetExeDir():
        return Binaries[0].OutputDir


    def CreateGlobalEnv(Toolchain, CompileEnv, LinkEnv):
        pass


    def CreateProjectCompileEnv():
        pass


    def SearchThroughDir(Dir, File):
        for Root, _, Files in os.walk(Dir):
            if File in Files:
                return os.path.join(Root, File)
        return None

    def IsUnderDir(Dir, File):
        for Root, _, Files in os.walk(Dir):
            if File in Files:
                return True
        return False



    # TODO: Add support for generated code!
    def FindModuleName(Name):

        # Check Project directory
        if Target._Project != None:
            ProjectDirSource = os.path.join(os.path.dirname(Target._Project), "Src")
            Temp = os.path.dirname(Target._Project)
        else:
            ProjectDirSource = ENGINEDIR
            Temp = ENGINEDIR

        ModuleFile = SearchThroughDir(ProjectDirSource, Name)

        if ModuleFile is not None:
            ModReader = ModuleReader.ModuleReader(ModuleFile)

            #TODO: Add generated code stuff here

            ModuleRet = ModuleBuilder.ModuleBuilder(ModReader, os.path.join(Temp, "Intermediate"))

            ModuleName_ModuleBuilder.append(ModReader.Name, ModuleRet)

            return ModuleRet

        return None

    @staticmethod
    def CreateBinName(Name, Platform, LinkType, Arch, BinType):

        Ret = ""

        if Platform == "Linux" and (BinType == "Dynamic" or BinType == "Static"):
            Ret = "lib"

        Ret = Ret + Name

        BuildPlatform = Platform.Platform.GetBuildPlatform(Platform)

        if BuildPlatform.NeedsArchSuffix() == True:
            Ret = Ret + Arch

        Ret = Ret + BuildPlatform.GetBinExtension(BinType)

        return Ret


    def CreateBinPaths(Dir, Name, Platform, LinkType, BinType, Arch, ExeSubFolder, ProjectFile, TargetFile):

        BinDir = os.path.join(Dir, "bin", Platform)

        if ExeSubFolder =! None and ExeSubFolder != "":
            BinDir = os.path.join(BinDir, ExeSubFolder)

        # Create full binary path with file name
        Bin = os.path.join(BinDir, CreateBinName(Name, Platform, LinkType, Arch, BinType))

        BuildPlatform = Platform.Platform.GetBuildPlatform(Platform)

        return BuildPlatform.FinalizeBinPaths(Bin, ProjectFile, TargetFile)



    def SetupBinaries():

        if Target.LaunchName == None or Target.LaunchName == "":
            raise ValueError("Launch name is None or blank")

        LaunchModule = FindModuleName(Target.LaunchName)

        if IsUnderDir(ENGINEDIR, LaunchModule) == True and Target.LinkType == "Monolithic":
            IntermediateDir = os.path.join(ENGINEDIR, PlatformIntermedFolder, Target.Name, BuildType)
        else:
            IntermediateDir = PlatformIntermed

        if Target.LinkType == "Monolithic" or Target.IntermediateType == "Unique":
            OutputDir = ProjectDir
        else:
            OutputDir = ENGINEDIR


        if target.IsDynamicLibrary == True and Target.LinkType == "Monolithic":
            CompileAsDynamic = True
        else:
            CompileAsDynamic = False

        if CompileAsDynamic == True:
            Temp1 = "Dynamic"
        else:
            Temp1 = "EXE"



        OutputList = CreateBinPaths(OutputDir, Target.Name, Target.LinkType, Arch, Temp1, Target.Arch, Target.BinSubPaths, Target._Project, Target)


        Bin = Binary.Binary(Temp1, OutputList, IntermediateDir, LaunchModule, Target, None, None) #FIXME: Haven't implemented Exports and Precompile, using none for now

        Binaries.append(Bin)

        LaunchModule.Binary = Bin

        Bin.Modules.append(LaunchModule)


    # Create's a TargetBuilder class based on StartingTarget
    @staticmethod
    def Create(StartingTarget, Target, UsePrecompiled):
        pass


    def Build(BuildConf, WorkingSet, AreWeAssembilingBuild):
        pass
