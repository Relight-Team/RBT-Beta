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

    def __init__(self, InSDK, InCEPlatform=CE.Platform.Linux, InPlatform="Linux"):
        super().__init__(InCEPlatform, InPlatform)
        self.SDK = InSDK

    def GetDefaultArch(self, ProjectFile):
        Ret = self.Arch

        if ProjectFile is None:
            EngineIni = None
        else:
            EngineIni = os.path.abspath(ProjectFile)

        # If abspath fails, we shall get it from command line instead
        if EngineIni is None:
            EngineIni = "../../../../BaseBuilder.cfg"  # TEMP SOLUTION
            pass  # FIXME: Get from command line, else get from BaseBuilder

        TempConfig = ConfigManager.ReadConfig(
            EngineIni, "PlatformInformation", "PlatformArch"
        )

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

    def MakeTargetValid(self, Target):

        if Target.UseAddressSanitizer is True or Target.UseThreadSanitizer is True:
            Target.Defines.append("FORCE_ANSI_ALLOCATOR=1")

    def ResetTarget(self, Target):
        self.MakeTargetValid(Target)

    def NeedsArchSuffix():
        return False

    def CanUseXGE():
        return False

    def CanParallelExecute():
        return True

    def IsBuildProduct(Name, TitlePrefixes, TitleSuffixes):

        if Name.startswith("lib"):
            if Platform.Platform.IsBuildProductName(
                Name, 3, len(Name) - 3, TitlePrefixes, TitleSuffixes, ".a"
            ) or Platform.Platform(
                Name, 3, len(Name) - 3, TitlePrefixes, TitleSuffixes, ".so"
            ):
                return True

        else:

            if (
                Platform.Platform.IsBuildProductNameNoIndex(
                    Name, TitlePrefixes, TitleSuffixes, ""
                )
                or Platform.Platform.IsBuildProductNameNoIndex(
                    Name, TitlePrefixes, TitleSuffixes, ".a"
                )
                or Platform.Platform.IsBuildProductNameNoIndex(
                    Name, TitlePrefixes, TitleSuffixes, ".so"
                )
            ):
                return True

    def GetBinExtension(InBinType):
        if InBinType == "EXE":
            return ""
        elif InBinType == "Dynamic":
            return ".so"
        elif InBinType == "Static":
            return ".a"
        else:
            return None

    def GetDebugExtensions(Target, InBinType):
        Ret = []

        if InBinType == "EXE":
            Ret = [".sym", ".debug"]

            if Target.SavePSYM is True:
                Ret.append(".pysm")

        return Ret

    def CheckEnvironmentConflicts(CompileEnv, LinkEnv):

        if CompileEnv.PGOOptimize != LinkEnv.PGOOptimize:
            raise ValueError("")

        if CompileEnv.PGOProfile != LinkEnv.PGOProfile:
            raise ValueError("")

        if CompileEnv.AllowLTCG != LinkEnv.AllowLTCG:
            raise ValueError("")

    def SetUpEnvironment(self, Target, CompileEnv, LinkEnv):

        BasePath = self.SDK.GetSDKArchPath(self.Target.Arch)

        if self.SDK._HostOS == "Linux" and (BasePath is None or BasePath == ""):
            CompileEnv.SysIncPaths.append("/usr/include")

        if CompileEnv.PGOProfile is True or CompileEnv.PGOOptimize is True:
            CompileEnv.AllowLTCG = True
            LinkEnv.AllowLTCG = True

        self.CheckEnvironmentConflicts(CompileEnv, LinkEnv)

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

    def CreateToolChain(self, InCppPlatform, Target):
        Options = LinuxToolchain.Options

        if Target.UseAddressSanitizer is True:
            Options.UseAddressSanitizer = True

        if Target.UseThreadSanitizer is True:
            Options.UseThreadSanitizer = True

        if Target.UseUnknownSanitizer is True:
            Options.UseUnknownSanitizer = True

        return LinuxToolchain.LinuxToolchain(self.Target.Arch, self.SDK, self.Target.SavePSYM, Options)

    def Deploy(Receipt):
        pass  # DEPLOY IS NOT SUPPORTED YET!
