import sys
import os

from Readers import ModuleReader

from Internal import CompileEnvironment

from Internal import FileBuilder

# Build's a module
class ModuleBuilder:

    Module = None

    AllFiles = []
    CompileFiles = []
    HeaderFiles = []

    IntermediateDir = ""
    SourceDir = "" # Directory for Module/Src
    Binary = None
    DependModules = []

    def __init__(self, InModule, InIntermediateDir):
        Module = InModule
        IntermediateDir = InIntermediateDir


    def GetSourceDir():
        Temp = Module.FilePath

        return os.path.abspath(os.path.join(Temp, "Src"))


    # FIXME: Add support for excluded folders
    def GetInfoFiles(self):

        Ret = []

        for Dirpath,_,filenames in os.walk(SourceDir):
            for f in filenames:
                Ret.append(os.path.abspath(os.path.join(Dirpath, f)))

        return Ret


    def SortLists(self):

        Temp = self.GetInfoFiles()

        for Item in Temp:
            Extension = os.path.splitext(Item)[1]

            if Extension == ".cpp".lower() or Extension == ".c".lower():
                CompileFiles.append(Item)

            elif Extension == ".h".lower() or Extension == ".hpp".lower():
                HeaderFiles.append(Item)

            AllFiles.append(Item)


    #FIXME: Add this once we add UNITY System
    def CreateUnityFile():
        pass


    # Return's true if everything is ok and doesn't clash with each other
    def DetectEngineModuleConflicts(self, ModuleName):

        EngineModuleOnlyOne = []

        if not ModuleName in EngineModuleOnlyOne:
            return True
        else:
            return False



    def CreateCompileEnv(Target, CompileEnv):
        NewCompile = CompileEnv

        CompileEnv.FalseUnityOverride = self.Modules.DisableUnity
        CompileEnv.UseRTTI |= self.Modules.RTTI
        CompileEnv.UseAVX = self.Modules.AVX

        CompileEnv.Defines.append(self.Modules.Defines)


    def AddToCompileEnv(Binary, IncludePathsList, SysIncludePathsList, DefinesList):

        IncludePathsList.append(self.Modules.ModuleDirectory)

        for Item in self.Modules.Includes:
            IncludePathsList.append(Item)

        for Item in self.Modules.SysIncludes:
            SysIncludePathsList.append(Item)

        for Item in self.Modules.Defines:
            DefinesList.append(Item)


    def SetupLinkEnv(self, Bin, LibPathList, AddLibList, RuntimeLibList, BinaryDependList, ExeDir, VisitedDependList):

        VDependList.append(self)

        if self in VDependList:

            if Binary != None and Binary != Bin and Binary not in BinaryDependList:
                BinaryDependList.append(Binary)

            if Bin != None and Bin.Type == "Static":
                IsStatic = True
            else:
                IsStatic = False

            if Binary != None and Binary.Type == "Static":
                IsModStatic = True
            else:
                IsModStatic = False

            if IsStatic == False and IsModStatic == True:

                for Item in DependModules:
                    IsExternal = isinstance(Item, ExternalBuilder)

                    IsItemStatic == False
                    if Item.Binary != None and Item.Binary.Type == "Static":
                        IsItemStatic = True

                    if IsExternal == True or IsItemStatic == True:
                        Item.SetupLinkEnv(Bin, LibPathList, AddLibList, RuntimeLibList, BinaryDependList, ExeDir, VisitedDependList)

            RuntimeLibList.append(self.Module.DynamicModulePaths)



    def CreateModule(self, RefChain, FuncName, FuncRefChain):

        if Module.FilePath == None or Module.FilePath == "":
            Temp = FuncName
        else:
            Temp = os.path.basename(Module.FilePath)

        NextChain = RefChain + " -> " + Temp

        CreateModuleName(Module.ModulesIncludes, RefChain, FuncName, FuncRefChain, OutputList)


    def CreateModuleName(self, ModuleNameList, RefChain, FuncName, FuncRefChain, OutputList):

        if OutputList == None:

            OutputList = []

            for Item in ModuleNameList:
                if not Item in OutputList:

                    self.CreateModule(RefChain, FuncName, FuncRefChain)
                    OutputList.append(Item)


    #FIXME: Quick hack thrown to ensure atleast the basics will work for the first testing. Once complete, please add these features
    # UNITY system, C++20 support, Precompiled headers, HeaderTool, Live Coding, Includes Header option
    def Compile(self, TargetReader, Toolchain, BinCompileEnv):

        Plat = BinCompileEnv.Plat

        LinkArray = []

        NewCompileEnv = CreateCompileEnv(Target, BinCompileEnv)

        UsingUnity = False

        #TODO: Add precompile implementation here

        Dict_SourceFiles = {}
        InputFiles = GetInfoFiles()

        #TODO: Add C++20 support, also Precompiled header stuff

        SourceFile_Unity = {}

        CPPFiles = []
        print("Well, you made it this far, yeah now we just need ModuleBuilder.Compile to set GenFiles")
        GenFiles = [] # FIXME: bro I just realize we need this to actually contain all our imput files cause right now it will always compile no input files!

        OutputActionList = []

        #FIXME: Replace this in an else statement for Unity files. Replace NewCompileEnv with Generated File Compile Environment
        LinkArray.append(Toolchain.CompileMultiArchCPPs(NewCompileEnv, GenFiles, IntermediateDir, OutputActionList))

        return LinkArray


class ExternalBuilder(ModuleBuilder):
    pass
