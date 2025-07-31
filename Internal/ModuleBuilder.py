import sys
import os

from Readers import ModuleReader

from Internal import CompileEnvironment

from Internal import FileBuilder


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

    def __init__(self, InModule, InIntermediateDir):
        self.Module = InModule
        self.IntermediateDir = InIntermediateDir

        self.SourceDir = os.path.join(self.Module.ModuleDirectory, "Src")

    def GetSourceDir(self):
        Temp = self.Module.FilePath

        return os.path.abspath(os.path.join(Temp, "Src"))

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

    def CreateCompileEnv(self, Target, CompileEnv):
        NewCompile = CompileEnv

        NewCompile.FalseUnityOverride = self.Module.DisableUnity
        NewCompile.UseRTTI |= self.Module.RTTI
        NewCompile.UseAVX = self.Module.AVX

        NewCompile.Defines.extend(self.Module.Defines)

        return NewCompile

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

            if self.Binary is not None and self.Binary != Bin and self.Binary not in BinaryDependList:
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

    def CreateModuleName(
        self, ModuleNameList, RefChain, FuncName, FuncRefChain, OutputList
    ):

        if OutputList is None:

            OutputList = []

            for Item in ModuleNameList:
                if Item not in OutputList:

                    self.CreateModule(RefChain, FuncName, FuncRefChain)
                    OutputList.append(Item)

    # FIXME: Quick hack thrown to ensure atleast the basics will work for the first testing. Once complete, please add these features
    # UNITY system, C++20 support, Precompiled headers, HeaderTool, Live Coding, Includes Header option
    def Compile(self, TargetReader, InToolchain, BinCompileEnv, FileBuilder):

        Plat = BinCompileEnv.Plat

        LinkArray = []

        NewCompileEnv = self.CreateCompileEnv(TargetReader, BinCompileEnv)

        UsingUnity = False

        # TODO: Add precompile implementation here

        Dict_SourceFiles = {}
        InputFiles = self.GetInfoFiles()

        # TODO: Add C++20 support, also Precompiled header stuff

        SourceFile_Unity = {}


        EveryFileToCompile = []

        GenFiles = (
            []
        )  # FIXME: bro I just realize we need this to actually contain all our input files cause right now it will always compile no input files!

        self.SortLists()

        EveryFileToCompile.extend(self.AllFiles)

        EveryFileToCompile.extend(GenFiles)

        print(self.AllFiles)

        OutputActionList = []

        if self.Module.ObjectName == None:
            ModName = self.Module.Name
        else:
            ModName = self.Module.ObjectName

        Intermed = os.path.join(self.IntermediateDir, "Build", str(Plat.value), TargetReader.Name, TargetReader.BuildType, ModName)

        # FIXME: Replace this in an else statement for Unity files. Replace NewCompileEnv with Generated File Compile Environment
        LinkArray.append(
            InToolchain.CompileMultiArchCPPs(
                NewCompileEnv, EveryFileToCompile, Intermed, OutputActionList
            )
        )

        for Item in OutputActionList:
            print("ITEM IN MODULEBUILDER CHECK: " + Item.Arguments)

        FileBuilder.ActionList.extend(OutputActionList)

        return LinkArray


class ExternalBuilder(ModuleBuilder):
    pass
