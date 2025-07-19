# FIXME: This test is shit, some of it works, some doesn't, maybe do this once you are done with it all?

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../Configuration")))

import Directory_Manager


sys.path.append(Directory_Manager.RBT_Directory)
sys.path.append(Directory_Manager.RBT_Directory + "/Template")

print("TESTING: PlatformSDK Parent Class")
print()

import PlatformSDK

SDK = PlatformSDK.PlatformSDK()

if SDK.SupportAutoSDK() == False:
    print("PlatformSDK.SupportAutoSDK() passed!")
else:
    raise ValueError(
        "Mismatch at PlatformSDK.SupportAutoSDK, should be False, instead we got "
        + SDK.SupportAutoSDK()
    )

PlatformSDK.PlatformSDK.AutoSDKEnabled()  # Should not cause errors

if SDK.AutoSDKSafe() == True:
    print("PlatformSDK.AutoSDKSafe() passed!")
else:
    raise ValueError(
        "PlatformSDK.AutoSDKSafe() should be safe by default (true), instead we got "
        + str(SDK.AutoSDKSafe())
    )

if SDK.GetRequiredSDKString() == "":
    print("PlatformSDK.GetRequiredSDKString() passed!")
else:
    raise ValueError(
        "PlatformSDK.GetRequiredSDKString() should be empty, instead we got "
        + SDK.GetRequiredSDKString()
    )

if SDK.GetTargetPlatformName() == "":
    print("PlatformSDK.GetTargetPlatformName() passed!")
else:
    raise ValueError(
        "PlatformSDK.GetTargetPlatformName() should be empty, instead we got "
        + SDK.GetTargetPlatformName()
    )

if SDK.PlatAutoSDKSetupEnvVar() == "AutoSDKSetup":
    print("PlatformSDK.PlatAutoSDKSetupEnvVar() passed!")
else:
    raise ValueError(
        "PlatformSDK.PlatAutoSDKSetupEnvVar() should've returnedd 'AutoSDKSetup, instead we got "
        + SDK.PlatAutoSDKSetupEnvVar()
    )

print(
    "PlatformSDK.GetCurrentlyInstalledSDK('Test') Result: "
    + SDK.GetCurrentlyInstalledSDK("Test")
)  # Should not cause errors

print(
    "PlatformSDK.GetLastRunScriptVersion('Test') Result: "
    + SDK.GetLastRunScriptVersion("Test")
)  # Should not cause errors

print(
    "PlatformSDK.SetCurrentlyInstalledSDK('SDKTest') Result: "
    + str(SDK.SetCurrentlyInstalledSDK("SDKTest"))
)

print("PlatformSDK.SetupManualSDK() Result: " + str(SDK.SetupManualSDK()))

print(
    "PlatformSDK.SetLastRunScriptVersion('Test') Result: "
    + str(SDK.SetLastRunScriptVersion("Test"))
)

if (
    SDK.GetHookExeName("Uninstaller") != "Undo_Setup.bat"
    and SDK.GetHookExeName("Uninstaller") != "Undo_Setup.sh"
):
    raise ValueError(
        "PlatformSDK.GetHookExeName(Uninstaller) should've been 'Undo_Setup.bat' or 'Undo_Setup.sh', instead we got "
        + SDK.GetHookExeName("Uninstaller")
    )
elif (
    SDK.GetHookExeName("Installer") != "Setup.bat"
    and SDK.GetHookExeName("Installer") != "Setup.sh"
):
    raise ValueError(
        "PlatformSDK.GetHookExeName(Installer) should've been 'Setup.bat' or 'Setup.sh', instead we got "
        + SDK.GetHookExeName("Installer")
    )
else:
    print("PlatformSDK.GetHookExeName() for both Installer and Uninstaller passed!")

SDK.RunAutoSDKHooks(
    "Test", "", "Uninstaller", True
)  # TODO: Find an actual application to test this with

print(
    "PlatformSDK.SetupEnvAutoSDK() Result: " + SDK.SetupEnvAutoSDK()
)  # Checks for errors for SetupEnvAutoSDK, SetupEnvAutoSDKFull(), and InvalidateInstalledAutoSDK

print(
    "PlatformSDK.HasRequiredAutoSDKInstalled() result: "
    + SDK.HasRequiredAutoSDKInstalled()
)

if SDK.HasSetupAutoSDK() != False:
    raise ValueError(
        "PlatformSDK.HasSetupAutoSDK() Should be False, instead we got "
        + str(SDK.HasSetupAutoSDK())
    )
else:
    print("PlatformSDK.HasSetupAutoSDK() passed!")

print("PlatformSDK.SetupManualSDK() Result: " + str(SDK.SetupManualSDK()))
