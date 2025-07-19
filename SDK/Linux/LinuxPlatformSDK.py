import importlib
import sys
import os

from . import Common

from Template import PlatformSDK

from Configuration import Directory_Manager


class LinuxPlatformSDK(PlatformSDK.PlatformSDK):

    SDKVersionRecommended = "Clang"

    TargetPlatformName = "Linux"

    VerboseCompiler = False

    VerboseLinker = False

    def GetRecommendedSDKVersion(self):
        return self.SDKVersionRecommended

    def GetTargetName(self):
        return self.TargetPlatformName

    def SDKVersionFileName(self):
        return "LinuxToolchainVersion.txt"

    # If true, then we can use the compiler installed on the system, otherwise we will use a local executable
    def CanUseSystemCompiler(self):
        if self._HostOS == "Linux":
            return True
        return False

    # FIXME: Find a way to make this work, and test both internal and external SDK
    def GetTreeSDKRoot(self):
        pass

    # Return's the location of the SDK, will either retrieve it from environment variable "LINUX_ROOT_MULTIARCH", or generate one if it isn't set
    def GetSDKLoc(self):

        Env = os.getenv("LINUX_ROOT_MULTIARCH")

        if Env == None or Env == "":
            Dir = self.GetTreeSDKRoot()

            if Dir != None and Dir != "":
                NewDir = os.path.join(Dir, self.SDKVersionFileName())

                if os.path.isdir(NewDir):
                    Env = NewDir

        return Env

    # Return's the location of the SDK for an arch
    def GetSDKArchPath(self, Arch):
        Env = self.GetSDKLoc()

        # If Environment is empty, we can get it from LINUX_ROOT
        if Env == None or Env == "":
            return str(os.environ.get("LINUX_ROOT"))

        # Else, we will get the directory from the LINUX_ROOT_MULTIARCH's archtecture path
        else:
            return str(os.path.join(Env, Arch))

    # Return's true if we found the Clang file
    def IsClangValid(self, BasePath):
        FilePath = os.path.join(BasePath, "bin")

        # TODO: Add Window's support

        FileName = "Clang++"

        File = os.path.join(FilePath, FileName)

        return os.path.exists(File)

    def InternalHasRequiredManualSDK(self):

        BasePath = GetSDKArchPath(Platform.DefaultArch)

        if not (BasePath == None or BasePath == ""):

            if IsClangValid(BasePath):
                return True

        if _HostOS == "Linux":
            if (Common.WhichClang() != None and Common.WhichClang() != "") and (
                Common.WhichGCC() != None and Common.WhichGCC() != ""
            ):
                return True

        return False
