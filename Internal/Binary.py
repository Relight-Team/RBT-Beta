from pathlib import Path

from . import ModuleBuilder
from . import CompileEnvironment
from . import LinkEnvironment

from . import Logger

# Class representation of a binary, can be dynamic, static, or executable. This will help us manage, compile, and link environments

class Binary:

    Type = "" # Can be EXE, Dynamic, or Static

    OutputDir = "" # The directory for our output

    OutputFilePaths = []

    IntermediateDir = "" # The directory all our modules will be compiled for

    LaunchModule = None # This is our launch module, will always be included if the configs allow us to

    Modules = [] # List of modules we will use for this binary, should be ModuleBuilder class

    ExportLibs = False # If true, we will export lib

    Precompiled = False # If Precompiled mode is activated

    AdditionalLibs = [] # Cashe of additional libraries we will link to binary


    def __init__(self, InType, InOutputFilePaths, InIntermediateDir, InLaunchModule, InExportLibs, InPrecompiled):
        Type = InType
        OutputFilePaths = InOutputFilePaths
        IntermediateDir = InIntermediateDir
        LaunchModule = InLaunchModule
        ExportLibs = InExportLibs
        Precompiled = InPrecompiled

        OutputDir = OutputFilePaths[0]
        Modules.append(LaunchModule)


    # Create all modules in the list
    def CreateModules(self, FuncName):

        for Item in Modules:
            Item.CreateModule(FuncName, "Target")


    # Adds the module to list if it doesn't exist
    def AddModule(self, InModule):
        if not InModule in Modules:
            Modules.append(InModule)


    # Returns the new Compile Environment that adds binary information from already existing compile environment
    def ReturnBinCompileEnv(self, OutputCompileEnv):

        CompileEnv = OutputCompileEnv

        if Type == "Dynamic":
            CompileEnv.IsDynamic = True

        if Type == "Static":
            CompileEnv.IsLibrary = True

        return CompileEnv




    # return's true if the path is contained in the parent
    def IsUnderDir(InPath, InParent):
        try:
            InputPath = Path(InPath).resolve(strict=False)
            InputDirectory = Path(InParent).resolve(strict=False)

            if InputDirectory in InputPath.parents or InputPath == InputDirectory:
                return True

        except:
            return False


    def CreateLinkEnv(self, Target, Toolchain, LinkEnv, CompileEnv, WorkingSet, ExeDir, FileBuilder):

        NewLinkEnv = LinkEnvironment.LinkEnvironment()

        NewLinkEnv.Dup(LinkEnv)

        LinkEnvModuleList = []

        BinList = []

        NewCompileEnv = ReturnBinCompileEnv(CompileEnv)

        if Target._Project != None and IsUnderDir(os.path.dirname(Target._Project), IntermediateDir) and NewCompileEnv.UseSharedBuildEnv == True:
            NewCompileEnv.UseSharedBuildEnv == False

        for Item in Modules:
            LinkFiles = []

            if Item.Binary == None or Item.Binary == self:
                LinkFiles = Item.Compile(Target, Toolchain, NewCompileEnv, FileBuilder) # Compile Module

                for LinkFilesItem in LinkFiles:

                    if not LinkFilesItem in NewLinkEnv.InputFiles:
                        NewLinkEnv.InputFiles.append(LinkFilesItem)

            else:

                BinList.append(Item.Binary)


            NewLinkEnv.OutputPaths = OutputFilePaths
            NewLinkEnv.IntermediateDir = IntermediateDir
            NewLinkEnv.OutputDir = OutputFilePaths[0]

            return NewLinkEnv


    # Create the binary, mainly involves compiling and linking. Returns output files
    def Build(self, TargetReader, Toolchain, CompileEnv, LinkEnv, ExeDir, FileBuilder):

        if Precompiled == True and TargetReader.LinkFilesTogether == True:
            return []

        BinLinkEnv = self.CreateLinkEnv()

        if TargetReader.LinkFilesTogether == False:
            return BinLinkEnv.InputFiles

        OutputFiles = []

        Exes = Toolchain.LinkEveryFiles(BinLinkEnv, False, FileBuilder.Actions)

        #TODO: Add ModuleNameToOutputItems FileBuilder function

        for Item in Exes:
            Temp = Toolchain.PostBuilt(Item, BinLinkEnv, FileBuilder.Actions)
            OutputFiles.append(Temp)

        return OutputFiles

    #FIXME: FINISH ME!
