import SDK.Linux.LinuxToolchain as Toolchain
import SDK.Linux.LinuxPlatformSDK as SDK
import Internal.Action as Action
import Internal.ActionExecute as Execute
import Internal.CompileEnvironment as CompileEnv
import Internal.LinkEnvironment as LinkEnv

import os

NewSDK = SDK.LinuxPlatformSDK()

NewToolchain = Toolchain.LinuxToolchain("x86", NewSDK)

NewConpileEnv = CompileEnv.CompileEnvironment("Linux", "Development", "x86")

ActionList = []


a = NewToolchain.CompileFiles(NewConpileEnv, ["/home/ethanboi/Desktop/Git/Ethanboilol/Relight-Engine/Programs/RelightBuildTool/Temp.cpp"], "/home/ethanboi/Desktop/Git/Ethanboilol/Relight-Engine/Programs/RelightBuildTool/BuildTest", "Test", ActionList)

NewLinkEnv = LinkEnv.LinkEnvironment()

NewLinkEnv.IntermediateDir = "/home/ethanboi/Desktop/Git/Ethanboilol/Relight-Engine/Programs/RelightBuildTool/BuildTest/"
NewLinkEnv.LocalShadowDir = "/home/ethanboi/Desktop/Git/Ethanboilol/Relight-Engine/Programs/RelightBuildTool/BuildTest/Shadow/"
NewLinkEnv.Arch = "x86_64"

Options = Toolchain.Options()

NewToolchain.Option = Options

NewLinkEnv.InputFiles.append("/home/ethanboi/Desktop/Git/Ethanboilol/Relight-Engine/Programs/RelightBuildTool/BuildTest/Temp.cpp.o")
NewLinkEnv.OutputPaths.append("/home/ethanboi/Desktop/Git/Ethanboilol/Relight-Engine/Programs/RelightBuildTool/BuildTest/Temp.bin")


NewToolchain.LinkFiles(NewLinkEnv, False, ActionList)

#NewExe = Execute.LinearExecuter()

#NewExe.ExecuteActionList(ActionList)

for I in ActionList:
    print("Command Path: " + I.CommandPath)
    print("Arguments:" + I.Arguments)
    print()


