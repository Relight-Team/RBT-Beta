import os

from . import ModuleBuilder
from . import Binary
from . import CompileEnvironment
from . import LinkEnvironment
from . import FileBuilder
from . import Logger


from Readers import ModuleReader
from Readers import TargetReader

from Template import Platform

from Configuration import Directory_Manager


# Builds a target, will use ModuleBuilder
class TargetBuilder:

    Target = None  # The TargetReader class

    PlatformIntermed = None  # Intermediate directory for the platform

    PlatformIntermedFolder = None  #

    EngineIntermed = None  # Intermediate directory for engine binary

    ProjectDir = None  # The project directory, if doesn't exist, we will use engine directory instead

    Binaries = []

    StartingTarget = None

    ModuleName_ModuleBuilder = {}

    def __init__(self, InStartingTarget, InTarget=None):
        self.StartingTarget = InStartingTarget
        self.Target = InTarget

        print("Arch = " + str(self.Target.Arch))

        self.PlatformIntermedFolder = TargetBuilder.GetIntermediateProject(
            self.StartingTarget.Platform, self.Target.Arch
        )

        # Overwrite target file with starting target properties
        if (
            self.StartingTarget.Modules != []
            and self.StartingTarget.Modules is not None
        ):
            self.Target.Modules = self.StartingTarget.Modules

        if self.Target._Project is not None and self.Target._Project != "":
            self.ProjectDir = os.path.dirname(self.Target._Project)
        else:
            self.ProjectDir = Directory_Manager.Engine_Directory

        self.PlatformIntermed = os.path.join(
            self.ProjectDir,
            self.PlatformIntermedFolder,
            self.Target.Name,
            self.Target.BuildType,
        )

        if self.Target.IntermediateType == "Unique":
            self.EngineIntermed = self.PlatformIntermed

        else:
            self.EngineIntermed = os.path.join(
                Directory_Manager.Engine_Directory,
                self.PlatformIntermed,
                self.Target.Name,
                self.Target.BuildType,
            )

    @staticmethod
    def GetIntermediateProject(Platform, Arch):
        return os.path.join("Intermediate", "Build", Platform, Arch)

    def CreateToolchain(self, InPlatform):

        if self.Target.ToolchainOverride is None:
            PlatformClassTemp = Platform.Platform.GetBuildPlatform(InPlatform)

            return PlatformClassTemp.CreateToolChain(InPlatform, self.Target)

        else:

            pass  # FIXME: Add support for ToolchainOverride

    def GetExeDir(self):
        return self.Binaries[0].OutputDir

    def IsEngineInstalled(self):
        InstalledEngineFileDir = os.path.join(
            Directory_Manager.Engine_Directory, "Build", "Installed.txt"
        )

        if os.path.isfile(InstalledEngineFileDir):
            return True
        else:
            return False

    # MASSIVE TODO: add more appends stuff once we add more options to target reader
    def AppendGlobalEnv(self, Toolchain, CompileEnv, LinkEnv):
        Toolchain.SetGlobalEnv(self.Target)

        # Append Global Compile Environment
        CompileEnv.Defines.extend(self.Target.Defines)
        CompileEnv.AdditionalArgs = self.Target.ExtraCompileArgs

        # Append Global Link Environment

        LinkEnv.AdditionalArgs = self.Target.ExtraLinkingArgs

        LinkInterTemp = os.path.join(
            Directory_Manager.Engine_Directory,
            self.PlatformIntermedFolder,
            self.Target.Name,
            self.Target.BuildType,
        )

        if self.IsEngineInstalled() or (
            self.Target._Project is not None and self.Target.LinkType == "Monolithic"
        ):
            if self.Target._Project is not None:
                LinkInterTemp = os.path.join(
                    os.path.dirname(self.Target._Project),
                    self.PlatformIntermedFolder,
                    self.Target.Name,
                    self.Target.BuildType,
                )
            # TODO: Add plugin support

        CompileEnv.UserIncPaths.append(Directory_Manager.Engine_Directory)

        LinkEnv.IntermediateDir = LinkInterTemp

        LinkEnv.OutputDir = LinkEnv.IntermediateDir

        LinkEnv.LocalShadowDir = LinkEnv.OutputDir

        # TODO: Add custom defines here for some target settings

        InPlatform = Platform.Platform.GetBuildPlatform(self.StartingTarget.Platform)

        InPlatform.SetUpEnvironment(self.Target, CompileEnv, LinkEnv)

        InPlatform.SetUpConfigEnv(self.Target, CompileEnv, LinkEnv)

    def CreateProjectCompileEnv(self):
        InPlatform = self.Platform.GetBuildPlatform(self.Target.platform)

        CPPPlatform = InPlatform.DefaultCPPPlatform

        CompileEnv = CompileEnvironment.CompileEnvironment(
            CPPPlatform.name, self.Target.BuildType, self.Target.Arch
        )
        LinkEnv = LinkEnvironment.LinkEnvironment(
            CPPPlatform.name, self.Target.BuildType, self.Target.Arch
        )

        Toolchain = self.CreateToolchain(CPPPlatform)
        self.AppendGlobalEnv(Toolchain, CompileEnv, LinkEnv)

        return CompileEnv

    def SearchThroughDir(self, Dir, TargetDir):
        for Root, SubDirList, Files in os.walk(Dir):
            if TargetDir in SubDirList:
                return os.path.join(Root, TargetDir)
        return None

    def IsUnderDir(self, Dir, File):
        Logger.Logger(
            1, "Checking if " + str(File) + " is under " + str(Dir) + ", please wait..."
        )
        for Root, _, Files in os.walk(Dir):
            if File in Files:
                return True
        return False

    # TODO: Add support for generated code!
    def FindModuleName(self, Name):

        # Check Project directory
        if self.Target._Project is not None:
            ProjectDirSource = os.path.join(
                os.path.dirname(self.Target._Project), "Src"
            )
            Temp = os.path.dirname(self.Target._Project)
        else:
            ProjectDirSource = Directory_Manager.Engine_Directory

        ModuleFile = self.SearchThroughDir(ProjectDirSource, Name)

        if ModuleFile is not None:
            FullModuleFile = os.path.join(ModuleFile, Name + ".Build")
            ModReader = ModuleReader.Module(FullModuleFile, self.StartingTarget)

            # TODO: Add generated code stuff here

            ModuleRet = ModuleBuilder.ModuleBuilder(
                ModReader, os.path.join(ProjectDirSource, "Intermediate"), self.Target, self.StartingTarget
            )

            self.ModuleName_ModuleBuilder[ModReader.Name] = ModuleRet

            return ModuleRet

        return None

    @staticmethod
    def CreateBinName(Name, InPlatform, LinkType, Arch, BinType):

        Ret = ""

        if InPlatform == "Linux" and (BinType == "Dynamic" or BinType == "Static"):
            Ret = "lib"

        Ret = Ret + Name

        BuildPlatform = Platform.Platform.GetBuildPlatform(InPlatform)

        if BuildPlatform.NeedsArchSuffix() is True:
            Ret = Ret + Arch

        Ret = Ret + BuildPlatform.GetBinExtension(BinType)

        return Ret

    def CreateBinPaths(
        self,
        Dir,
        Name,
        InPlatform,
        LinkType,
        BinType,
        Arch,
        ExeSubFolder,
        ProjectFile,
        TargetFile,
    ):

        BinDir = os.path.join(Dir, "bin", InPlatform)

        if ExeSubFolder is not None and ExeSubFolder != "":
            BinDir = os.path.join(BinDir, ExeSubFolder)

        # Create full binary path with file name
        Bin = os.path.join(
            BinDir,
            TargetBuilder.CreateBinName(Name, InPlatform, LinkType, Arch, BinType),
        )

        BuildPlatform = Platform.Platform.GetBuildPlatform(InPlatform)

        return BuildPlatform.FinalizeBinPaths(Bin, ProjectFile, TargetFile)

    def SetupBinaries(self):

        if self.Target.IncludeLaunch == True and (
            self.Target.LaunchName is None or self.Target.LaunchName == ""
        ):
            Logger.Logger(5, "Launch name is None or blank")

        if self.Target.IncludeLaunch == True:
            LaunchModule = self.FindModuleName(self.Target.LaunchName)
        else:
            # If we don't have Launch Module, just use the first module
            LaunchModule = self.FindModuleName(self.Target.Modules[0])

        if (
            self.IsUnderDir(
                Directory_Manager.Engine_Directory, LaunchModule.Module.FilePath
            )
            is True
            and self.Target.LinkType == "Monolithic"
        ):
            #GetIntermediateModule()
            IntermediateDir = os.path.join(
                Directory_Manager.Engine_Directory,
                self.PlatformIntermedFolder,
                self.Target.Name,
                self.BuildType,
            )
        else:
            IntermediateDir = self.PlatformIntermed

        if (
            self.Target.LinkType == "Monolithic"
            or self.Target.IntermediateType == "Unique"
        ):
            OutputDir = self.ProjectDir
        else:
            OutputDir = Directory_Manager.Engine_Directory

        if (
            self.Target.IsDynamicLibrary is True
            and self.Target.LinkType == "Monolithic"
        ):
            CompileAsDynamic = True
        else:
            CompileAsDynamic = False

        if CompileAsDynamic is True:
            Temp1 = "Dynamic"
        else:
            Temp1 = "EXE"

        OutputList = self.CreateBinPaths(
            OutputDir,
            self.Target.Name,
            self.StartingTarget.Platform,
            self.Target.LinkType,
            Temp1,
            self.Target.Arch,
            self.Target.BinSubPaths,
            self.Target._Project,
            self.Target,
        )

        Bin = Binary.Binary(
            Temp1, OutputList, IntermediateDir, LaunchModule, None, None
        )  # FIXME: Haven't implemented Exports and Precompile, using none for now

        self.Binaries.append(Bin)

        LaunchModule.Binary = Bin

        Bin.Modules.append(LaunchModule)

    @staticmethod
    def CreateTargetReaderFromTargetName(TargetName, StartingTarget, ProjectFile=None):

        # if Project File is defined, search in that directory, otherwise we will search through engine directory
        if ProjectFile is not None:
            DirToSearch = os.path.dirname(ProjectFile)
        else:
            DirToSearch = Directory_Manager.Engine_Directory

        # If we have -TargetDir set, then it will always overwrite everything else

        if StartingTarget.TargetDir is not None:
            DirToSearch = StartingTarget.TargetDir

        TargetSearchDir = os.path.join(DirToSearch)

        RetFile = None

        Logger.Logger(1, "Searching For Target File at: " + TargetSearchDir)
        # Search through directory
        # TODO: Unoptimized, since this will check every single file to see if it's a target file, is there an Optimized way?
        for RootDir, SubDirList, FilesList in os.walk(TargetSearchDir):
            for File in FilesList:
                if File == TargetName + ".Target":
                    RetFile = os.path.join(RootDir, File)

        if RetFile is None:
            Logger.Logger(5, "We could not find " + TargetName + ".Target")

        Logger.Logger(1, "Target file found: " + RetFile)

        Ret = TargetReader.Target(RetFile, StartingTarget, ProjectFile)

        return Ret

    def SetupPreBuild(self):
        self.SetupBinaries()

    # Create's a TargetBuilder class based on StartingTarget
    @staticmethod
    def Create(StartingTarget, UsePrecompiled):
        TargetReader = TargetBuilder.CreateTargetReaderFromTargetName(
            StartingTarget.Name, StartingTarget, StartingTarget.Project
        )

        # TODO: Add precompile support here

        Ret = TargetBuilder(StartingTarget, TargetReader)

        Ret.SetupPreBuild()

        return Ret

    # Build's the target, uses binary class to compile the files
    # FIXME: Just like with ModuleBuilder, this is a quick hack thrown to ensure at least the basics will work for the first testing. Once complete, please add these features
    # UNITY system, C++20 support, Precompiled headers, HeaderTool, Live Coding, Includes Header option
    def Build(self, BuildConf, WorkingSet, AreWeAssembilingBuild):

        BinOriginal = []

        Plat = Platform.Platform.GetBuildPlatform(self.StartingTarget.Platform)

        CppPlat = Plat.DefaultCPPPlatform

        CompileEnv = CompileEnvironment.CompileEnvironment(
            CppPlat, self.Target.BuildType, self.Target.Arch
        )

        # Set

        LinkEnv = LinkEnvironment.LinkEnvironment(
            CompileEnv.Plat, CompileEnv.Conf, CompileEnv.Arch
        )

        Toolchain = self.CreateToolchain(CppPlat.value)

        self.AppendGlobalEnv(Toolchain, CompileEnv, LinkEnv)

        InFileBuilder = FileBuilder.FileBuilder()

        # FIXME: Add binary filter

        # FIXME: Add plugin support

        # FIXME: Add code here that will let exe know all modules included if using monolithic

        # FIXME: Add code that tells the exe where the engine dir is and put it in compile defines

        # FIXME: Add UObject support and generated code support

        ExeOutputDir = self.GetExeDir()

        OutputItems = []

        # Compile each binary

        for Item in self.Binaries:

            BinOutput = Item.Build(
                self.Target, Toolchain, CompileEnv, LinkEnv, ExeOutputDir, InFileBuilder
            )

        # FIXME: Add runtime depends support

        # FIXME: Add precompile Plugin support

        # FIXME: Add metadata support

        return InFileBuilder
