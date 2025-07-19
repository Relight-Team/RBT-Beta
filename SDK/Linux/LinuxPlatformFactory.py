import os
import sys

import LinuxPlatform
import LinuxPlatformSDK

sys.path.append("../../Template")

import PlatformFactory


class LinuxFactory(PlatformFactory.FactorySDK):

    # Return's the target platform for this factory
    def TargetPlatform():
        return "Linux"

    # Register the Build Platform w/ Platform Class
    def RegBuildPlatform():

        SDK = LinuxPlatformSDK.LinuxPlatformSDK()

        SDK.ManageAndValidate()

        # TODO: FINISH ONCE GENERATE PROJECT FILES IS FINISHED
