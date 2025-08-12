import sys
import os

from Readers import ModuleReader

from Internal import CompileEnvironment

from Internal import FileBuilder

from Internal import Logger

from Configuration import Directory_Manager


# Build's a module
class ModuleBuilder:

    # Module reader
    Module = None

    AllFiles = []
    CompileFiles = []
    HeaderFiles = []

    IntermediateDir = ""
    SourceDir = ""  # Directory for Module/Src
    Binary = None
    DependModules = []
    TargetReader = None
    StartingTarget = None

    def __init__(self, InModule, InIntermediateDir, TargetReader, StartingTarget):
        self.Module = InModule
        self.IntermediateDir = InIntermediateDir
        self.TargetReader = TargetReader
        self.StartingTarget = StartingTarget

        # HACK fix: if module is engine and isn't unique, then we will always set intermediate to engine dir
        if self.Module.IsEngineModule is True and self.TargetReader.IntermediateType is not "Unique":
            self.IntermediateDir = os.path.join(Directory_Manager.Engine_Directory, "Intermediate")

        self.SourceDir = os.path.join(self.Module.ModuleDirectory, "Src")

    # Get the module's Source Directory
    def GetSourceDir(self):
        Temp = self.Module.FilePath

        return os.path.abspath(os.path.join(Temp, "Src"))

    # Returns an array of every file in the Source Directory
    # FIXME: Add support for excluded folders
    def GetInfoFiles(self):

        Ret = []

        for Dirpath, _, filenames in os.walk(self.SourceDir):
            for f in filenames:
                Ret.append(os.path.abspath(os.path.join(Dirpath, f)))

        return Ret

    # Get all input files, sort them between Compile, Header, and Generated file
    def SortLists(self):

        Temp = self.GetInfoFiles()

        for Item in Temp:
            Extension = os.path.splitext(Item)[1]

            if Extension == ".cpp".lower() or Extension == ".c".lower():
                self.CompileFiles.append(Item)

            elif Extension == ".h".lower() or Extension == ".hpp".lower():
                self.HeaderFiles.append(Item)

            self.AllFiles.append(Item)

    # FIXME: Add this once we add UNITY System
    def CreateUnityFile():
        pass

    # Return's true if everything is ok and doesn't clash with each other
    def DetectEngineModuleConflicts(self, ModuleName):

        EngineModuleOnlyOne = []

        if ModuleName not in EngineModuleOnlyOne:
            return True
        else:
            return False

    # Return's a new Compile Environment, set's up new compile environment based on Module settings
    def CreateCompileEnv(self, Target, CompileEnv):
        NewCompile = CompileEnv

        NewCompile.FalseUnityOverride = self.Module.DisableUnity
        NewCompile.UseRTTI |= self.Module.RTTI
        NewCompile.UseAVX = self.Module.AVX

        NewCompile.Defines.extend(self.Module.Defines)

        NewCompile.AdditionalLibs.extend(self.Module.AdditionalLibs)

        NewCompile.UserIncPaths.extend(self.Module.Includes)

        return NewCompile

    # Append Compile Environment based on Function Arguments
    def AddToCompileEnv(
        self, Binary, IncludePathsList, SysIncludePathsList, DefinesList
    ):

        IncludePathsList.append(self.Modules.ModuleDirectory)

        for Item in self.Modules.Includes:
            IncludePathsList.append(Item)

        for Item in self.Modules.SysIncludes:
            SysIncludePathsList.append(Item)

        for Item in self.Modules.Defines:
            DefinesList.append(Item)

    # Append DynamicModulePaths to RuntimeLibList
    def SetupLinkEnv(
        self,
        Bin,
        LibPathList,
        AddLibList,
        RuntimeLibList,
        BinaryDependList,
        ExeDir,
        VDependList,
    ):

        VDependList.append(self)

        if self in VDependList:

            if (
                self.Binary is not None
                and self.Binary != Bin
                and self.Binary not in BinaryDependList
            ):
                BinaryDependList.append(self.Binary)

            if Bin is not None and Bin.Type == "Static":
                IsStatic = True
            else:
                IsStatic = False

            if self.Binary is not None and self.Binary.Type == "Static":
                IsModStatic = True
            else:
                IsModStatic = False

            if IsStatic is False and IsModStatic is True:

                for Item in self.DependModules:
                    IsExternal = isinstance(Item, ExternalBuilder)

                    IsItemStatic = False
                    if Item.Binary is not None and Item.Binary.Type == "Static":
                        IsItemStatic = True

                    if IsExternal is True or IsItemStatic is True:
                        Item.SetupLinkEnv(
                            Bin,
                            LibPathList,
                            AddLibList,
                            RuntimeLibList,
                            BinaryDependList,
                            ExeDir,
                            VDependList,
                        )

            RuntimeLibList.append(self.Module.DynamicModulePaths)

    # Create a module
    def CreateModule(self, RefChain, FuncName, FuncRefChain):

        if self.Module.FilePath is None or self.Module.FilePath == "":
            Temp = FuncName
        else:
            Temp = os.path.basename(self.Module.FilePath)

        NextChain = RefChain + " -> " + Temp

        OutputList = []

        self.CreateModuleName(
            self.Module.ModulesIncludes, RefChain, FuncName, FuncRefChain, OutputList
        )

    # Create a module
    def CreateModuleName(
        self, ModuleNameList, RefChain, FuncName, FuncRefChain, OutputList
    ):

        if OutputList is None:

            OutputList = []

            for Item in ModuleNameList:
                if Item not in OutputList:

                    self.CreateModule(RefChain, FuncName, FuncRefChain)
                    OutputList.append(Item)

    # Returns the full file path if file exist in directory, return's none otherwise
    def SearchThroughDir(self, Dir, SubDir):
        for Root, SubDirList, Files in os.walk(Dir):
            if SubDir in Files:
                return os.path.join(Root, SubDir)
        return None

    # Finds the .Build file
    def FindModuleReaderFile(self, TargetReader, ModuleName):

        SearchModule = os.path.join(os.path.basename(ModuleName) + ".Build")

        # First, check the project/Target directory itself
        if TargetReader._Project is not None:
            DirCheck = os.path.dirname(TargetReader._Project)
            FullDir = os.path.join(DirCheck, "Src")
        else:
            DirCheck = os.path.dirname(TargetReader.FilePath)
            FullDir = DirCheck

        # Scan if the dir exist

        SubDir = self.SearchThroughDir(FullDir, SearchModule)

        # If we cannot find it, then it's most likely in the Engine Directory
        if SubDir is None:
            DirCheck = Directory_Manager.Engine_Directory

            FullDir = os.path.join(DirCheck)
            SubDir2 = self.SearchThroughDir(FullDir, SearchModule)

            # If this still fails, we shall through an error
            if SubDir2 is None:
                Logger.Logger(
                    5,
                    "We could not find Module "
                    + SearchModule
                    + " in either ProjectDir, TargetDir, and EngineDir, please check your modules and try again!",
                )
            else:
                return SubDir2
        else:
            return SubDir

    def IfListInSecondList(self, List1, List2):

        Ret = all(Item in List1 for Item in List2)

        return Ret

    # Run the Compile function for each Modules
    def GetAndCompileDependencies(
        self,
        InModuleBuilder,
        TargetReader,
        InToolchain,
        BinCompileEnv,
        FileBuilder,
        AlreadyBuiltModulesList,
    ):

        BinCompileEnv.UserIncPaths.append(
            (os.path.join(os.path.dirname(self.Module.FilePath), "Src"))
        )  # Includes module to be linked

        if InModuleBuilder.Module.Modules:
            for Item in InModuleBuilder.Module.Modules:

                FilePathName = self.FindModuleReaderFile(TargetReader, Item)

                SubModuleReader = ModuleReader.Module(FilePathName, self.StartingTarget)

                if FilePathName not in AlreadyBuiltModulesList:
                    AlreadyBuiltModulesList.append(FilePathName)

                    NewModuleBuilder = ModuleBuilder(
                        SubModuleReader, self.IntermediateDir, self.TargetReader, self.StartingTarget
                    )

                    self.GetAndCompileDependencies(
                        NewModuleBuilder,
                        TargetReader,
                        InToolchain,
                        BinCompileEnv,
                        FileBuilder,
                        AlreadyBuiltModulesList,
                    )

                    NewModuleBuilder.Compile(
                        TargetReader,
                        InToolchain,
                        BinCompileEnv,
                        FileBuilder,
                        AlreadyBuiltModulesList,
                    )

    # Compile's the Module
    # FIXME: Quick hack thrown to ensure atleast the basics will work for the first testing. Once complete, please add these features
    # UNITY system, C++20 support, Precompiled headers, HeaderTool, Live Coding, Includes Header option
    def Compile(
        self,
        TargetReader,
        InToolchain,
        BinCompileEnv,
        FileBuilder,
        AlreadyBuiltModulesList,
    ):

        self.CompileFiles = []
        self.HeaderFiles = []
        self.AllFiles = []

        Plat = BinCompileEnv.Plat

        LinkArray = []

        NewCompileEnv = self.CreateCompileEnv(TargetReader, BinCompileEnv)

        UsingUnity = False

        self.SortLists()

        # Compile 3rd party modules

        Logger.Logger(1, "Start Collecting Third Party dependencies for " + self.Module.Name)
        for ThirdParty in self.Module.ThirdParty:
            Logger.Logger(3, "Searching for third party module: " + ThirdParty)
            ThirdPartyFile = self.FindModuleReaderFile(TargetReader, ThirdParty)
            Logger.Logger(1, "File found: " + ThirdPartyFile)

            ThirdPartyReader = ModuleReader.Module(ThirdPartyFile, self.StartingTarget)

            ThirdPartyBuilder = ExternalBuilder(ThirdPartyReader, self.IntermediateDir, TargetReader)

            AdditionalLibs = ThirdPartyBuilder.Compile()

            LinkArray.extend(AdditionalLibs)

            NewCompileEnv.AdditionalLibs.extend(AdditionalLibs)
            NewCompileEnv.UserIncPaths.extend(ThirdPartyReader.Includes)
            NewCompileEnv.SysIncPaths.extend(ThirdPartyReader.SysIncludes)

        # TODO: Add precompile implementation here

        Dict_SourceFiles = {}
        InputFiles = self.GetInfoFiles()

        self.GetAndCompileDependencies(
            self,
            TargetReader,
            InToolchain,
            BinCompileEnv,
            FileBuilder,
            AlreadyBuiltModulesList,
        )

        # get each item in module list from this module
        if (
            self.Module.Modules is True
            and self.IfListInSecondList(AlreadyBuiltModulesList, self.Module.Modules)
            is True
        ):
            self.GetAndCompileDependencies(
                self,
                TargetReader,
                InToolchain,
                BinCompileEnv,
                FileBuilder,
                AlreadyBuiltModulesList,
            )

        # TODO: Add C++20 support, also Precompiled header stuff

        SourceFile_Unity = {}

        EveryFileToCompile = []

        GenFiles = (
            []
        )  # FIXME: bro I just realize we need this to actually contain all our input files cause right now it will always compile no input files!

        EveryFileToCompile.extend(self.CompileFiles)

        EveryFileToCompile.extend(GenFiles)

        OutputActionList = []

        if self.Module.ObjectName == None or self.Module.ObjectName == "":
            ModName = self.Module.Name
        else:
            ModName = self.Module.ObjectName

        # If module doesn't have name, result in error

        if ModName == None:
            Logger.Logger(5, "Module Name and/or Module Short Name is None, we cannot continue! Module Name: (" + str(self.Module.Name) + "), Module Short Name: (" + str(self.Module.ObjectName)) + ")"

        if ModName == "":
            Logger.Logger(5, "Module Name and/or Module Short Name is empty, we cannot continue! Module Name: (" + str(self.Module.Name) + "), Module Short Name: (" + str(self.Module.ObjectName)) + ")"

        Intermed = os.path.join(
            self.IntermediateDir,
            "Build",
            str(Plat.value),
            TargetReader.Arch,
            TargetReader.Name,
            TargetReader.BuildType,
            ModName,
        )

        # FIXME: Replace this in an else statement for Unity files. Replace NewCompileEnv with Generated File Compile Environment
        LinkArray.extend(
            InToolchain.CompileMultiArchCPPs(
                NewCompileEnv, EveryFileToCompile, Intermed, OutputActionList
            )
        )

        FileBuilder.ActionList.extend(OutputActionList)

        # BUGFIX: Clear input files, so that if we are compiling multiple modules, it won't add extra to different Intermediate

        self.CompileFiles = []

        return LinkArray


class ExternalBuilder(ModuleBuilder):

    # Module reader
    Module = None

    AllFiles = []
    CompileFiles = []
    HeaderFiles = []

    IntermediateDir = ""
    SourceDir = ""  # Directory for Module/Src
    TargetReader = None

    def __init__(self, InModule, InIntermediateDir, TargetReader):
        self.Module = InModule
        self.IntermediateDir = os.path.join(InIntermediateDir, "ThirdParty")
        self.TargetReader = TargetReader

        # HACK fix: if module is engine and isn't unique, then we will always set intermediate to engine dir
        if self.Module.IsEngineModule is True and self.TargetReader.IntermediateType is not "Unique":
            self.IntermediateDir = os.path.join(Directory_Manager.Engine_Directory, "Intermediate", "ThirdParty")

        self.SourceDir = os.path.dirname(self.Module.FilePath)


    def Compile(
        self
    ):


        # Run 3rd party script
        for Command in self.Module.CommandToRun:
            os.system(Command)

        return self.Module.AdditionalLibs



