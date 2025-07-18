import os
import platform
import sys
import subprocess
import inspect
import importlib

from Internal import CompileEnvironment as CE
from Internal import ConfigManager as ConfigM
from Internal import Logger


from Configuration import TargetPlatforms as TP

from . import PlatformFactory as PF

EngineDir = "../.."

ConfigDir = EngineDir + "/Configs"

_HostOS = platform.system()

# A class that stores information on the platform
class PlatformInfo:

    Platform = ConfigM.ReadConfig(ConfigDir + "/BaseBuilder.cfg", "PlatformInformation", "PlatformName")
    Arch = ConfigM.ReadConfig(ConfigDir + "/BaseBuilder.cfg", "PlatformInformation", "PlatformArch")

    # Import the FactorySDK file based on the config
    @staticmethod
    def ImportFactory():

        Logger.Logger(0, "Running ImportFactory() from PlatformInfo")

        if os.path.isfile(EngineDir + "/Programs/RelightBuildTool/SDK/" + PlatformInfo.Platform + "/" + PlatformInfo.Platform + "PlatformFactory"):
            Logger.Logger(1, "Platform Factory found in base SDK directory: " + EngineDir + "/Programs/RelightBuildTool/SDK/" + PlatformInfo.Platform + "/" + PlatformInfo.Platform + "PlatformFactory.py")
            return importlib.import_module(EngineDir + "/Programs/RelightBuildTool/SDK/" + PlatformInfo.Platform + "/" + PlatformInfo.Platform + "PlatformFactory")

        elif os.path.isfile(EngineDir + "/Extras/CustomSDK/" + PlatformInfo.Platform + "/" + PlatformInfo.Platform + "PlatformFactory"):
            Logger.Logger(1, "Platform Factory found in Custom SDK directory: " + EngineDir + "/Extras/CustomSDK/" + PlatformInfo.Platform + "/" + PlatformInfo.Platform + "PlatformFactory.py")
            return importlib.import_module(EngineDir + "/Extras/CustomSDK/" + PlatformInfo.Platform + "/" + PlatformInfo.Platform + "PlatformFactory")
        else:
            Logger.Logger(5, "Couldn't find " + PlatformInfo.Platform + "/" + PlatformInfo.Platform + "PlatformFactory.py in either RelightBuildTool's SDK directory or CustomSDK directory")

    # Return true if the config file's platform value is valid
    @staticmethod
    def IsValid(InPlatform):
        Logger.Logger(0, "Running IsValid(" + InPlatform + ")")
        if InPlatform == "Linux":
            Logger.Logger(1, "Returned True")
            return True

        elif PlatformInfo.Platform == InPlatform:
            Logger.Logger(1, "Returned True")
            return True
        Logger.Logger(1, "Returned False")
        return False

class Platform:

    BuildPlatform = {}

    PlatformGroup = {}

    Plat = ""

    DefaultCPPPlatform = CE.Platform

    PlatformCachedFolder = []

    IncludeCachedFolder = []

    ExcludeCachedFolder = []

    def __init__(self, InPlatform, InCppPlatform):
        Plat = InPlatform
        DefaultCPPPlatform = InCppPlatform

    # Create PlatformFactory instance and run the class's "RegBuildPlatform" function
    @staticmethod
    def RegPlatform(IncNonInstalledPlats):


        Logger.Logger(0, "Running RegPlatform(" + IncNonInstalledPlats + ")")

        Module = PlatformInfo.ImportFactory()

        Types = []

        # Store each Factory class from the FactorySDK file into types

        for Name, Object in inspect.getmembers(Module):

            if inspect.isclass(Object):

                Types.append(Object)

        # For each instance, run the RegBuildPlatform
        for T in Types:
            if isinstance(T, PF.FactorySDK):

                TempInit = T()

                if IncNonInstalledPlats == True or PlatformInfo.IsValid(TempInit.TargetPlatform()) == True:
                    Logger.Logger(1, "Registering " + TempInit.TargetPlatform() + " to Types")
                    TempInit.RegBuildPlatform()


    # Return's the array of platform folders
    @staticmethod
    def GetPlatformFolders():
        Logger.Logger(0, "Running GetPlatformFolders()")
        if PlatformCachedFolder == None or PlatformCachedFolder == []:
            PlatFolder = []

            for i in TP.TargetPlatform:
                if TP.Valid(i) == True:
                    PlatFolder.append(i)

            for i in TP.TargetGroupPlatform:
                PlatFolder.append(i)

            PlatformCachedFolder = PlatFolder

        Logger.Logger(1, "Running GetPlatformFolders()")
        return PlatformCachedFolder

    # Return's all folders that we are going to include for this platform
    def GetIncludeFolders():
        Logger.Logger(0, "Running GetIncludeFolders()")
        if IncludeCachedFolder == None or IncludeCachedFolder == []:
            IncFolder = []

            IncFolder.append(Plat)

            temp = TP.GetPlatformGroup(Plat)
            for i in TP.ReturnTargetGroupVar(temp):
                IncFolder.append(i)

            IncludeCachedFolder = IncFolder

        return IncludeCachedFolder

    # Return's all folder that we are going to exclude for this platform
    def GetExcludeFolders():
        Logger.Logger(0, "Running GetExcludeFolders()")
        if ExcludeCachedFolder == None or ExcludeCachedFolder == []:
            ExcludeCachedFolder = GetPlatformFolders().difference(GetIncludeFolders)

        return ExcludeCachedFolder

    # Return's true if we have the required SDK installed on this device
    def HasRequiredSDK():
        pass # Will be overwritten with child class

    # Return's all platforms that are registered
    @staticmethod
    def GetRegPlatforms():
        Logger.Logger(0, "Running GetRegPlatforms()")
        List = []
        for Key in ReturnGroupDict():
            List.append(Key)
        return List

    # Return's the default architecture
    def GetDefaultArch(ProjectFile):
        return ""

    # Return's the folder name of the architecture
    def GetFolderNameArch(Arch):
        Logger.Logger(0, "Platform class's arch is " + Arch)
        return Arch

    # Finds all build files and directories to clean, store these files and directories in CleanFiles and CleanDirs
    def DetectBuildFilesToClean(BaseDir, TitlePrefixes, TitleSuffixes, CleanFiles, CleanDirs):
        for Item in BaseDir:
            if os.path.isfile(os.path.join(BaseDir, Item)): # if it's a file
                if IsBuildProduct(Item, TitlePrefixes, TitleSuffixes) or IsFileDefaultBuildProduct(Item, TitlePrefixes, TitleSuffixes):
                    CleanFiles.append(Item)

            if os.path.isdir(os.path.join(BaseDir, Item)): #if it's a directory
                if IsBuildProduct(Item, TitlePrefixes, TitleSuffixes):
                    CleanDirs.append(Item)

                else:
                    DetectBuildFilesToClean(Item, TitlePrefixes, TitleSuffixes, CleanFiles, CleanDirs)


    # Find any additional files to clean, store these files and directories in CleanFiles and CleanDirs
    def DetectAdditionalBuildToClean(Target, CleanFiles, CleanDirs):
        pass # Will be overwritten with child class

    # If The Build Product Name is the RBT's default build prodcut
    @staticmethod
    def IsFileDefaultBuildProduct(Name, TitlePrefixes, TitleSuffixes):
        if IsBuildProductName(Name, TitlePrefixes, TitleSuffixes, ".CompileTarget") or IsBuildProductName(Name, TitlePrefixes, TitleSuffixes, ".CompileModule") or IsBuildProductName(Name, TitlePrefixes, TitleSuffixes, ".CompileVersion"):
            return True
        return False

    # return's true if the name is the same as RBT's build product for the target
    @staticmethod
    def IsBuildProduct(Name, TitlePrefixes, TitleSuffixes):
        pass # Will be overwritten with child class

    # Return's true if the name is the main RBT name format without extension
    # Example: Test-Linux-Debug.so
    @staticmethod
    def IsBuildProductName(Name, Index, SubInt, TitlePrefixes, TitleSuffixes, Extension):
        if SubInt > len(Extension):
            tmp = Name[Index + SubInt - len(Extension): Index + SubInt] # Substring
            if tmp.lower() == Extension.lower():

                return IsBuildProductName(Name, Index, SubInt - len(Extension), TitlePrefixes, TitleSuffixes)
        return False

    # Return's true if the name is the main RBT name format without extension
    # Example: Test-Linux-Debug.so
    @staticmethod
    def IsBuildProductNameNoExtension(Name, Index, SubInt, TitlePrefixes, TitleSuffixes):
        for Prefix in TitlePrefixes:

            if SubInt >= len(Prefix):
                tmp = Name[Index: Index + len(Prefix)]
                if tmp.lower() == Prefix.lower():
                    MinIndex = Index + len(Prefix)

                    for Suffix in TitleSuffixes:
                        MaxIndex = Index + Count - len(Suffix)
                        tmp = Name[MaxIndex: MaxIndex + len(Suffix)]

                        if MinIndex >= MaxIndex and tmp.lower() == Suffix.lower():
                            if MinIndex < MaxIndex and Name[MinIndex] == '-':

                                MinIndex += 1

                                while MinIndex < MaxIndex and Name[MinIndex] != "-" and Name[MinIndex] != ".":
                                    MinIndex += 1

                            if MinIndex == MaxIndex:
                                return True

        return False

    # Return's true if the name is the main RBT name format without extension
    # Example: Test-Linux-Debug.so
    @staticmethod
    def IsBuildProductNameNoIndex(Name, TitlePrefixes, TitleSuffixes, Extension):
        return IsBuildProductName(Name, 0, len(Name), TitlePrefixes, TitleSuffixes, Extension)

    # Stuff to execute after the build process has been done but before we sync the target platform (which is when we prepare and transfer build artifacts to the target platform)
    def PostBuildBeforeSync(Target):
        pass # Will be overwritten with child class

    # Return the bundle directory for the Link Environment
    def GetBundleDir(Target, FileOutputs):
        return None

    # Return's true if the plaform can be used
    @staticmethod
    def CanUsePlatform(Platform):
        for I in TP.TargetPlatform:
            if I.name.lower == Platform.lower:
                return True

        return False

    #  Set Input to BuildPlatform instance
    @staticmethod
    def RegBuildPlatform(InBuildPlatform):
        BuildPlatform[InBuildPlatform.name] = InBuildPlatform.value

    # Set PlatformGroup to the input group key with the value of input build platform
    @staticmethod
    def RegBuildPlatformGroup(InBuildPlatform, InBuildPlatformGroup):
        Plat = []

        Plat.append(InBuildPlatform)

        PlatformGroup[InBuildPlatformGroup] = Plat

    # Return's all groups with the given platform
    @staticmethod
    def GetAllGroupsWithPlatform(Platform):
        GroupList = []

        for Group in TP.TargetGroupPlatform:
            PlatList = Group.value

            for Platfor in PlatList:
                if Platfor.name.lower == Platform.lower:
                    GroupList.append(Platfor.name)
        return GroupList

    # Return's the BuildPlatform value if it exist, return's None if we allow failure, otherwise it will raise an error
    @staticmethod
    def GetBuildPlatform(InPlatform, AllowFailure=False):
        if InPlatform in BuildPlatform:
            return BuildPlatform[InPlatform]
        elif AllowFailure == True:
            return None
        else:
            Logger.Logger(5, "BuildPlatform does not has key '" + str(InPlatform) + "' when running GetBuildPlatform")

    # modify each Module in BuildPlatform
    @staticmethod
    def ModifyHostModuleConfig(ModName, Target, Module):
        for Item in BuildPlatform:
            Tmp = Item.value
            Tmp.ActivePlatformModuleRulesToModify(ModName, Target, Module)


    # modify each moudle in the target
    def ActivePlatformModuleRulesToModify(ModName, Target, Module):
        pass # Will be overwritten with child class

    # return's the Delimiter based on the platform
    @staticmethod
    def GetPathDelimiter():
        if _HostOS == "Windows":
            return ";"
        else:
            return ":"

    # Return's the platform is
    def GetPlatformName(self):
        return self.__class__.__name__

    # Return's if this platform supports XGE (Incredibuild or equivalent)
    def CanUseXGE():
        return True

    # Return's if this platform supports multiple execution at once
    def CanParallelExecute():
        return CanUseXGE()

    # If the platform support distributed compilation (Distcc, DMUCS, etc)
    def CanUseDistcc():
        return False

    # If this platform support's SN-DBS (SN System's Distributed Build Server)
    def CanUseSNDBS():
        return False

    # Set the new target to platform-specific defaults
    def ResetTarget(Target):
        pass # Will be overwritten with child class

    # Validate the Target File
    def MakeTargetValid(Target):
        pass # Will be overwritten with child class

    # Return's if the platform requires a monolithic build (All modules into a single binary)
    @staticmethod
    def RequireMonolithicBuild(InPlatform, InConfig):
        BuildPlat = GetBuildPlatform(InPlatform, True)
        if BuildPlat is not None:
            return ShouldCompileMonolithic(InPlatform)

        return False

    # Return's the platform binary extension based on the bin type
    def GetBinExtension(InBinType):
        return None

    # Return's the extension for debug info based on bin type
    def GetDebugExtension(Target, InBinType):
        return None

    # If we should make the compile Monolithic if the config file is not set
    def ShouldCompileMonolithic(Name, Target, Module):
        return False

    # Returns if we should override whether to append the arch to bin name
    def NeedsArchSuffix():
        return True

    # Return's the array of binary output files (by default, it will only return 1 item)
    def FinalizeBinPaths(BinName, ProjectFile, Target):
        Tmp = []
        Tmp.append(BinName)
        return Tmp

    # Return the array of configs we are using
    def GetConfig(Target, IncludeDebug):
        Config = []

        Config.append("Development")

        if IncludeDebug == True:
            Config.insert(0, "Debug")

        return Config

    # Return's true if the Project Settings are the same as the defualt settings
    @staticmethod
    def IsProjectSettingsDefault(Platform, ProjectDir, Section, IntKeys, BoolKeys, StringKeys):
        pass #TODO: DO ONCE FINISH CONFIG

    # Returns if we have the following default build config settings
    def HasDefaultBuildConfig(Platform, ProjectDir):
        pass

    # Returns if we required a build
    def RequiresBuild(Platform, ProjectDir):
        return False

    # Add the extra modules the platform requires, wihtout exposing information about the platform
    def AddExtraModules(Target, ModuleNames):
        pass # Will be overwritten with child class

    # Setup the target environment
    def SetUpEnvironment(Target, CompileEnv, LinkEnv):
        pass # Will be overwritten with child class

    # Setup the config enviornment
    def SetUpConfigEnv(Target, CompileEnv, LinkEnv):
        # This if statement is for 3rd party only, as some of them require this define to access debug features
        if CompileEnv.UseDebugCRT == True:
            CompileEnv.Defines.append("_DEBUG=1")
        else:
            CompileEnv.Defines.append("NDEBUG=1")

        # Set Define based on why type of build it is
        if Target.BuildType == "Debug":
            CompileEnv.Defines.append("RE_BUILDTYPE_DEBUG=1")

        elif Target.BuildType == "Development":
            CompileEnv.Defines.append("RE_BUILDTYPE_DEVELOPMENT=1")

        elif Target.BuildType == "Final":
            CompileEnv.Defines.append("RE_BUILDTYPE_FINAL=1")


        # Set Debug info to true if we are using debug

        if not Target.DisableDebugInfo and ShouldCreateDebugInfo(Target):
            CompileEnv.AddDebugInfo = True

        LinkEnv.AddDebugInfo = CompileEnv.AddDebugInfo


    # returns metadata that is not tracked
    def GetExternalBuildMetadata(ProjectFile):
        pass # Will be overwritten with child class

    # Return's true if platform is in group
    @staticmethod
    def IsPlatformInGroup(Platform, Group):
        Plat = TP.ReturnTargetGroupVar(Group)

        if Plat is not None and Platform in Plat:
            return True
        return False

    # If we should Create debug information if the config file is not set
    def ShouldCreateDebugInfo(Target):
        pass # Will be overwritten with child class

    # Create the platfomr's toolchain instance
    def CreateToolChain(InCppPlatform, Target):
        pass # Will be overwritten with child class

    # Deploy the target
    def Deploy(Receipt):
        pass # Will be overwritten with child class
