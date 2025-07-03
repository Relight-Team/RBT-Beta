import os
import sys

from . import LinuxPlatformSDK
from . import LinuxToolchain
from . import Common

from Template import Platform

from Internal import CompileEnvironment as CE
from Internal import ConfigManager
from Internal import Logger


class LinuxPlatform(Platform.Platform):

    Arch = ""

    SDK = LinuxPlatformSDK.LinuxPlatformSDK()

    def __init__(InSDK, InCEPlatform=CE.Platform.Linux, InPlatform="Linux"):
        super().__init__(InCEPlatform, InPlatform)
        SDK = InSDK


    def GetDefaultArch(ProjectFile):
        Ret = Arch

        if ProjectFile == None:
            EngineIni = None
        else:
            EngineIni = os.path.abspath(ProjectFile)

        # If abspath fails, we shall get it from command line instead
        if EngineIni == None:
            EngineIni = "../../../../BaseBuilder.cfg" # TEMP SOLUTION
            pass #FIXME: Get from command line, else get from BaseBuilder

        TempConfig = ConfigManager.ReadConfig(EngineIni, "PlatformInformation", "PlatformArch")

        # TODO: Shitty hack to ensure compatibility, idk if this even works, if it doesn't FIX IT!
        if "X86-64".lower() in TempConfig:
            Ret = "x86_64-unknown-linux-gnu"

        elif "Arch".lower() in TempConfig and "Aarch64" not in TempConfig:
            Ret = "arm-unknown-linux-gnueabihf"

        elif "Aarch64".lower() in TempConfig:
            Ret = "aarch64-unknown-linux-gnueabi"

        elif "i386".lower() in TempConfig:
            Ret = "i686-unknown-linux-gnu"

        else:
            print("Using default arch")

        return Ret


    def MakeTargetValid(Target):

        if Target.UseAddressSanitizer == True or Target.UseThreadSanitizer == True:
            Target.Defines.append("FORCE_ANSI_ALLOCATOR=1")


    def ResetTarget(Target):
        MakeTargetValid(Target)

    def NeedsArchSuffix():
        return False

    def CanUseXGE():
        return False

    def CanParallelExecute():
        return True

    def IsBuildProduct(Name, TitlePrefixes, TitleSuffixes):

        if Name.startswith("lib"):
            if Platform.Platform.IsBuildProductName(Name, 3, len(Name) - 3, TitlePrefixes, TitleSuffixes, ".a") or Platform.Platform(Name, 3, len(Name) - 3, TitlePrefixes, TitleSuffixes, ".so"):
                return True

        else:

            if Platform.Platform.IsBuildProductNameNoIndex(Name, TitlePrefixes, TitleSuffixes, "") or Platform.Platform.IsBuildProductNameNoIndex(Name, TitlePrefixes, TitleSuffixes, ".a") or Platform.Platform.IsBuildProductNameNoIndex(Name, TitlePrefixes, TitleSuffixes, ".so"):
                return True


    def GetBinExtension(InBinType):
        if BinType == "EXE":
            return ""
        elif BinType == "Dynamic":
            return ".so"
        elif BinType == "Static":
            return ".a"
        else:
            return None


    def GetDebugExtensions(Target, InBinType):
        Ret = []

        if InBinType == "EXE":
            Ret = [".sym", ".debug"]

            if Target.SavePSYM == True:
                Ret.append(".pysm")

        return Ret



    def CheckEnvironmentConflicts(CompileEnv, LinkEnv):

        if CompileEnv.PGOOptimize != LinkEnv.PGOOptimize:
            raise ValueError("")

        if CompileEnv.PGOProfile != LinkEnv.PGOProfile:
            raise ValueError("")

        if CompileEnv.AllowLTCG != LinkEnv.AllowLTCG:
            raise ValueError("")


    def SetUpEnvironment(Target, CompileEnv, LinkEnv):

        BasePath = SDK.GetSDKArchPath(Target.Arch)

        if SDK._HostOS == "Linux" and (BasePath == None or BasePath == ""):
            CompileEnv.SysIncPaths.append("/usr/include")

        if CompileEnv.PGOProfile == True or CompileEnv.PGOOptimize == True:
            CompileEnv.AllowLTCG = True
            LinkEnv.AllowLTCG = True

        CheckEnvironmentConflicts(CompileEnv, LinkEnv)

        if Target.LinkType == "Monolithic":
            CompileEnv.HideSymbols = True

        LinkEnv.AdditionalLibs.append("pthread")

        CompileEnv.Defines.append("RE_PLATFORM_LINUX=1")
        CompileEnv.Defines.append("RE_PLATFORM_UNIX=1")

        # For libraries
        CompileEnv.Defines.append("LINUX=1")


    def ShouldCreateDebugInfo(Target):
        if Target.BuildType == "Final":
            return False
        else:
            return True


    def CreateToolChain(InCppPlatform, Target):
        Options = LinuxToolchain.Options

        if Target.UseAddressSanitizer = True:
            Options.UseAddressSanitizer = True

        if Target.UseThreadSanitizer = True:
            Options.UseThreadSanitizer = True

        if Target.UseUnknownSanitizer = True:
            Options.UseUnknownSanitizer = True

        return LinuxToolchain.LinuxToolchain(Target.Arch, SDK, Target.SavePSYM, Options)


    def Deploy(Receipt):
        pass # DEPLOY IS NOT SUPPORTED YET!
