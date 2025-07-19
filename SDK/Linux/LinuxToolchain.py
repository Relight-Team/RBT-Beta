import importlib
import os
import re
import subprocess
import sys
import platform

from . import LinuxPlatformSDK
from . import Common

from Template import Toolchain


from Internal import CompileEnvironment
from Internal import Action
from Internal import File_Manager
from Internal import Logger

from Configuration import Directory_Manager as Dir_Manager


class Options:

    UseAddressSanitizer = False

    UseThreadSanitizer = False

    UseUnknownSanitizer = False

    def IsNone(self):
        if (
            self.UseAddressSanitizer == False
            and self.UseThreadSanitizer == False
            and UseUnknownSanitizer == False
        ):
            return True
        return False


class LinuxToolchain(Toolchain.ToolchainSDK):

    # The Architecture
    Arch = ""

    # If true, we should NOT produce PIE exe by default
    NotUsingPIE = False

    # If true, we should save PYSM (portable symbol files) that was produced by dump_syms
    SavePYSM = False

    # Information we will print for debug info
    Info = ""

    Version = [0, 0, 0]

    VersionString = ""

    # Cashe variables
    IsCrossCompiling = None
    MultiArchRoot = ""
    BasePath = ""
    ClangPath = ""
    GCCPath = ""
    ArPath = ""
    LlvmArPath = ""
    RanLibPath = ""
    StripPath = ""
    ObjectCopyPath = ""
    DumpSymsPath = ""
    BreakpadEncoderPath = ""

    UseFixedDepends = False

    Bin = []

    HasPrintedDetails = False

    CanUseSystemCompiler = False

    # If we already used LLD
    _LldUsed = False

    _HostOS = platform.system()

    SDK = LinuxPlatformSDK.LinuxPlatformSDK()

    Option = Options

    def __init__(
        self, InArch, InSDK, InSavePYSM=False, InOptions=None, InPlatform=None
    ):

        Logger.Logger(3, "Using Linux Toolchain")

        # If InPlatform is none, we will use Linux, otherwise we will use InPlatform
        if InPlatform == None:
            self._RunBase(
                InArch, InSDK, CompileEnvironment.Platform.Linux, InSavePYSM, InOptions
            )
        else:
            self._RunBase(InArch, InSDK, InPlatform, InSavePYSM, InOptions)

        self.MultiArchRoot = self.SDK.GetSDKLoc()
        self.BasePath = self.SDK.GetSDKArchPath(self.Arch)

        CanUseSystemCompiler = self.SDK.CanUseSystemCompiler()
        IsCompilerValid = False

        if CanUseSystemCompiler == False and (
            self.BasePath == None or self.BasePath == ""
        ):
            raise ValueError("ERROR: LINUX_ROOT environment variable is not set!")

        self.DumpSymsPath = os.path.join(
            Dir_Manager.Engine_Directory, "bin", "Linux", "DumpSyms"
        )
        self.BreakpadEncoderPath = os.path.join(
            Dir_Manager.Engine_Directory, "bin", "Linux", "BreakpadEncoder"
        )

        if (self.BasePath != None or self.BasePath != "") and (
            self.MultiArchRoot == None or self.MultiArchRoot == ""
        ):
            self.MultiArchRoot = self.BasePath

        # Validate the Compiler if we are using a system, but the compiler isn't valid
        if CanUseSystemCompiler == True and IsCompilerValid == False:
            # self.ClangPath = os.path.join(self.BasePath, "bin", "clang++") # FIXME: Doesn't work in this prototype, using WhichClang() as temp solution
            self.ClangPath = Common.WhichClang()
            self.GCCPath = Common.WhichGCC()
            self.ArPath = Common.WhichAR()
            self.llvmArPath = Common.WhichLLVM()
            self.RanLibPath = Common.WhichRanLib()
            self.StripPath = Common.WhichStrip()
            self.ObjectCopyPath = Common.WhichObjCopy()

            # FixDepends supports only on windows
            if self._HostOS == "Windows":
                self.UseFixedDepends = True

            # if the currently running OS is Linux, we will ensure all lang types are overwritten by POSIX ASCII only system
            if self._HostOS == "Linux":
                os.environ["LC_ALL"] = "C"

            # These settings allow us to cross compile
            self.IsCrossCompiling == True

            # FIXME: Make sure this is accuate once we add it!
            self.IsCompilerValid = self.GetCompilerVersion()

        # Validate system Toolchain
        self._ValidateSystemToolchain()

        # Check the compiler settings
        self.SetDefaultCompilerSettings()

        # TODO: Add proper detection
        self._LldUsed = True

    # Validate system Toolchain
    def _ValidateSystemToolchain(self):
        if self.CanUseSystemCompiler == True and self.IsCompilerValid == False:
            self.ClangPath = Common.WhichClang()
            self.GCCPath = Common.WhichGCC()
            self.ArPath = Common.WhichAR()
            self.llvmArPath = Common.WhichLLVM()
            self.RanLibPath = Common.WhichRanLib()
            self.StripPath = Common.WhichStrip()
            self.ObjectCopyPath = Common.WhichObjCopy()

            self.UseFixedDepends = False

            # These settings allow us to cross compile
            self.IsCrossCompiling == False

            # FIXME: Make sure this is accuate once we add it!
            self.IsCompilerValid = GetCompilerVersion()

    # Run's the parent init and set some values
    def _RunBase(self, InArch, InSDK, InPlatform, InSavePYSM=False, InOptions=None):
        super().__init__(InPlatform)
        self.Arch = InArch
        self.SDK = InSDK
        self.SavePYSM = InSavePYSM
        self.Option = InOptions

    # Return's true if we are using clang
    def IsUsingClang(self):
        if self.ClangPath is not None and self.ClangPath != "":
            return True
        return False

    # Set the array version from string
    def SetVersionArray(self):
        VersionArrayString = Version.split(".")

        tmp = 0

        while tmp < len(VersionArrayString) - 1:
            self.Version[tmp] = int(VersionArrayString[tmp])
            tmp += 1

    def GetEncodeCommand(self, LinkEnv, OutputFile):
        # FIXME: Add Windows Support!

        OutputFileFullLoc = os.path.abspath(OutputFile)  # Get full file path

        OutputFileWithoutExt = os.path.splitext(OutputFileFullLoc)[
            0
        ]  # Removes the extension

        EncodeSymbolFile = os.path.join(
            LinkEnv.OutputDir, OutputFileWithoutExt + ".sym"
        )

        SymbolFile = os.path.join(LinkEnv.LocalShadowDir, OutputFile + ".pysm")

        StripFile = os.path.join(LinkEnv.LocalShadowDir, OutputFile + "_nodebug")

        DebugFile = os.path.join(LinkEnv.OutputDir, OutputFileWithoutExt + ".debug")

        # If SavePYSM is true, then we will store the symbol file in the output directory instead of the shadow directory
        if self.SavePYSM == True:
            SymbolFile = os.path.join(LinkEnv.OutputDir, OutputFileWithoutExt + ".pysm")

        # Compile dump_syms
        Ret = (
            '"'
            + self.DumpSymsPath
            + '" -c -o "'
            + OutputFileFullLoc
            + '" "'
            + os.path.abspath(SymbolFile)
            + '"\n'
        )

        # encode breakpad symbols
        Ret += (
            '"'
            + self.BreakpadEncoderPath
            + '" "'
            + os.path.abspath(SymbolFile)
            + '" "'
            + os.path.abspath(EncodeSymbolFile)
            + '" \n'
        )

        # Write debug information
        if LinkEnv.AddDebugInfo == True:

            # use objcopy on strip file
            Ret += (
                '"'
                + self.ObjectCopyPath
                + '" --strip-all "'
                + os.path.abspath(OutputFile)
                + '" "'
                + os.path.abspath(StripFile)
                + '"\n'
            )

            # use objcopy on debug file
            Ret += (
                '"'
                + self.ObjectCopyPath
                + '" --only-keep-debug "'
                + os.path.abspath(OutputFile)
                + '" "'
                + os.path.abspath(DebugFile)
                + '"\n'
            )

            # use objcopy to link Debug file to the Final .so file, using temp to avoid corruption
            Ret += (
                '"'
                + self.ObjectCopyPath
                + '" --add-gnu-debuglink="'
                + os.path.abspath(DebugFile)
                + '" "'
                + os.path.abspath(StripFile)
                + '" "'
                + os.path.abspath(OutputFile)
                + '.temp" \n'
            )

            # Rename the .temp to the final name

            Ret += (
                'mv "'
                + os.path.abspath(OutputFile)
                + '.temp" "'
                + os.path.abspath(OutputFile)
                + '"\n'
            )

            # Change permission to normal (this permission allows main user to read and write, but other users can only read it)
            Ret += 'chmod 644 "' + os.path.abspath(DebugFile) + '"\n'

        else:

            Ret += '"' + StripFile + '" "' + os.path.abspath(OutputFile) + '"'

        return Ret

    def GetCompilerVersion(self):
        # Check Clang
        if self.ClangPath != "":
            App = subprocess.run(
                [self.ClangPath, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

            Out = App.stdout

            Match = re.search(r"clang version (\d+\.\d+(\.\d+)?)", Out)

            if Match:
                self.VersionString = Match.group(1)

    def SetDefaultCompilerSettings(self):
        if self.ClangPath != "":

            App = subprocess.run(
                "echo '' | " + self.ClangPath + " -E -dM -",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                shell=True,
            )

            for Line in App.stdout:
                LineStrip = Line.strip()

                if LineStrip == None or LineStrip == "":
                    break

                if "__pie__" in LineStrip or "__PIE__" in LineStrip:
                    self.NotUsingPIE = True

    # Set switches depending on architecture
    @staticmethod
    def ArchSwitch(Arch):
        if Arch.startswith("arm") or Arch.startswith("aarch64"):
            return " -fsigned-char"  # Tells the compiler to treat char as signed chars
        return ""

    # Set defines based on the architecture
    @staticmethod
    def ArchDefine(Arch):
        if Arch.startswith("x86_64") or Arch.startswith("aarch64"):
            return " -D_LINUX64"
        return ""

    @staticmethod
    def UseLibCXX(Arch):
        Override = os.environ.get("RBT_Use_LibCXX", "0")

        # If Override is valid
        if Override == None or Override == "":

            # If Override is true
            if Override == "True" or Override == "true" or Override == "1":

                # If Override starts with supported arch, return true
                if (
                    Override.startswith("i686")
                    or Override.startswith("x86_64")
                    or Override.startswith("aarch64")
                ):
                    return True

        return False

    # Fix the args to make it compatable
    @staticmethod
    def EscapeArgs(Arg):
        ArgArray = Arg.split("=")

        try:
            Key = ArgArray[0]
        except:
            Key = None

        try:
            Value = ArgArray[1]
        except:
            Value = None

        if Key == None:
            return ""

        else:

            if not Value.startswith('"') and (" " in Value or "$" in Value):
                Value = Value.trim('"')
                Value = '"' + Value + '"'

            Value.replace('"', '\\"')

        if Value == None:
            return Key
        else:
            return Key + "=" + Value

    @staticmethod
    def ArgCPP():
        return " -x c++ -std=c++14"

    @staticmethod
    def ArgPCH():
        return " -x c++-header -std=c++14"

    # Whether to use llvm-ar or ar
    # TODO: Temp solution, assumes it's system-wide, add support for non-system wide
    def ArchiveProgram():
        if LlvmArPath != "":
            return "llvm-ar"
        elif ArPath != "":
            return "ar"
        else:
            raise ValueError("Cannot create llvm-ar or ar. Both tools cannot be found")

    def ArgArchive():
        return " rcs"

    def UsingLld(self, Arch):
        if self._LldUsed == True and Arch.startswith("x86_64"):
            return True
        return False

    def CanAdvanceFeatures(self, Arch):
        if self.UsingLld(Arch) == True:
            if LlvmArPath != None and LlvmArPath != "":
                return True
        return False

    def SDKVersionCorrect():
        pass

    def GetResponseName(self, LinkEnv, OutputFile):
        return os.path.join(
            LinkEnv.IntermediateDir, os.path.basename(OutputFile) + ".rsp"
        )

    def ArchiveAndIndex(LinkEnv, OutputActionList):
        Archive = Action.Action

        Archive.CommandPath = ArchiveProgram()

        Archive.Arguments = "-c '"

        Archive.CreateImportLib = True

        OutputFile = LinkEnv.OutputDir
        Archive.OutputItems.append(OutputFile)

        Arg = ' "' + ArPath + '" ' + ArgArchive + ' "' + os.path.abspath(OutputFile)
        Archive.Arguments += Arg

        InputFiles = []

        for File in LinkEnv.InputFiles:
            Temp = os.path.abspath(File)
            ImputFiles.append('"' + Temp + '"')

        ResponsePath = self.GetResponseName(LinkEnv, OutputFile)

        # FIXME: Add support for not generating project files support (Requires class that doesn't exist yet) This will create intermediate file and add it to precondition list

        if LlvmArPath == None or LlvmArPath == "":
            Archive.Arguments += (
                ' && "' + self.RanlibPath + '" "' + os.path.abspath(OutputFile) + '"'
            )

        Archive.Arguments += " " + LinkEnv.AdditionalArgs

        Archive.Arguments += "'"

        OutputActionList.append(Archive)

        return OutputFile

    # FIXME: ADD IMPORTS AFTER ADDING CXX LIBRARY!
    def _ImportCXX(self, Arch):
        Ret = ""
        CanUse = self.UseLibCXX(Arch)
        if CanUse == True:
            Ret += "-nostdinc++"
        return Ret

    def _AddSanitize(self):
        Ret = ""
        if self.Option != None and self.Option.UseAddressSanitizer == True:
            Ret += " -fsanitize=address"
        if self.Option != None and self.Option.UseThreadSanitizer == True:
            Ret += " -fsanitize=thread"
        if self.Option != None and self.Option.UseUnknownSanitizer == True:
            Ret += " -fsanitize=undefined"
        return Ret

    def _Global_Clang_Flags(self):
        Ret = " -Wno-tautological-compare -Wno-unused-private-field --Wno-undefined-bool-conversion"
        return Ret

    def _Optimize(self, CompileEnv):
        if CompileEnv.Optimize == False:
            Ret = " -O0"
        elif (
            self.Option.UseAddressSanitizer == True
            or self.Option.UseTreeadSanitizer == True
        ):
            Ret = " -O1 -g"

            if self.OptionUseAddressSanitizer == True:
                Ret += " -fno-optimize-sibling-calls -fno-omit-frame-pointer"
        else:

            Ret = " -O2"

        return Ret

    def _OutputConfig(self, Config):
        Ret = ""
        if Config == "Final":
            Ret = " -Wno-unused-value -fomit-frame-pointer"
        elif Config == "Debug":
            Ret = " -fno-inline -fno-omit-frame-pointer -fstack-protector"
        return Ret

    def _Exceptions(self, Bool):
        if Bool == True:
            Ret = " -fexceptions -DUSE_EXCEPTIONS=1"
        else:
            Ret = " -fno-exceptions"

        return Ret

    def _CrossCompile(self, Arch):
        Ret = ""

        if self.IsCrossCompiling == False:
            return ""

        if self.IsUsingClang == True and (Arch != None or Arch != ""):
            Ret += " -target " + Arch

        # Ret += ' --sysroot="' + self.BasePath + '"' # FIXME: This breaks my current code, since we are using system shit for now, once I replace those code, re-add this

        return Ret

    # Global Arguments that we will use for both Compiling and Linking
    def GetGlobalArg(self, CompileEnv):
        Ret = " -c -pipe"

        Ret += self._ImportCXX(CompileEnv.Arch)

        Ret += self._AddSanitize()

        Ret += " -Wall -Werror"

        if not CompileEnv.Arch.startswith("X86_64") and CompileEnv.Arch.startswith(
            "AARCH64"
        ):
            Ret += " -funwind-tables"

        Ret += (
            " -Wsequence-point -Wdelete-non-virtual-dtor"
            + self.ArchSwitch(CompileEnv.Arch)
            + " -fno-math-errno"
        )

        if CompileEnv.HideSymbols == True:
            Ret += " -fvisibility=hidden -fvisibility-inlines-hidden"

        # TODO: Add GCC Support

        if self.IsUsingClang == True:

            Ret += self._Global_Clang_Flags()

        Ret += " -Wno-unused-variable -Wno-unused-function -Wno-switch -Wno-unknown-pragmas -Wno-gnu-string-literal-operator-template -Wno-invalid-offsetof"

        if CompileEnv.PGOOptimize == True:
            Ret += (
                ' -Wno-backend-plugin -fprofile-instr-use="'
                + os.path.join(CompileEnv.PGODirectory, CompileEnv.PGOFilePrefix)
                + '"'
            )

        elif CompileEnv.PGOProfile == True:
            Ret += " -fprofile-generate"

        if CompileEnv.ShadowVariableWarnings == True:
            Ret += " -Wshadow"

            if CompileEnv.ShadowVariableAsError == False:
                Ret += " -Wno-error=shadow"

        if CompileEnv.UndefinedIdentifierWarnings == True:
            Ret += " -Wundef"

            if CompileEnv.UndefinedIdentifierAsError == False:
                Ret += " -Wno-error=undef"

        Ret += self._OutputConfig(CompileEnv.Conf)

        if CompileEnv.UseInlining == False:
            Ret += " -fno-inline-functions"

        if CompileEnv.IsDynamic == True:
            Ret += " -fPIC -ftls-model=local-dynamic"

        Ret += self._Exceptions(CompileEnv.ExceptionHandling)

        if self.NotUsingPIE == True and CompileEnv.IsDynamic == False:
            Ret += " -fno-PIE"

        if self.SDK.VerboseCompiler == True:
            Ret += " -v"

        Ret += self.ArchDefine(CompileEnv.Arch)

        Ret += self._CrossCompile(CompileEnv.Arch)

        return Ret

    def _SetPrintedDetails(self, CompileEnv):
        if self.HasPrintedDetails == False:
            self.Print(CompileEnv)

            if self.MultiArchRoot != None and self.MultiArchRoot != "":
                if self.SDKVersionCorrect == False:
                    raise ValueError("FATAL: ThirdParty for Linux is incomplete!")

            self.HasPrintedDetails == True

    # Compiles the list of files together
    def CompileFiles(
        self, CompileEnv, InputFilesList, DirOutput, Name, OutputActionList
    ):
        Logger.Logger(1, "Name: " + Name)
        Logger.Logger(1, "Input Files List: " + str(InputFilesList))
        Logger.Logger(1, "Directory Output: " + DirOutput)

        Args = self.GetGlobalArg(CompileEnv)

        PCH = ""

        self._SetPrintedDetails(CompileEnv)

        if self.CanAdvanceFeatures(CompileEnv.Arch) == False:
            if CompileEnv.AllowLTCG == True or CompileEnv.PGOOptimize == True:
                Logger.Logger(
                    5,
                    "LTCG and/or PGO Optimize cannot be true if we are not allowed to use advance features!",
                )

        if CompileEnv.PCH_Act == CompileEnvironment.PCHAction.Include:
            PCH += " -include " + CompileEnv.PCHIncludeName

        for Item in CompileEnv.UserIncPaths:
            Args += " -I" + Item

        for Item in CompileEnv.SysIncPaths:
            Args += " -I" + Item

        for Item in CompileEnv.Defines:
            Args += " -D" + EscapeArgs(Item)

        CPPOut = CompileEnvironment.Output

        for Item in InputFilesList:

            NewAction = Action.Action()

            NewAction.PreconditionItems.append(CompileEnv.ForceIncFiles)

            NewArgs = ""

            Extension = (os.path.splitext(os.path.abspath(Item))[1]).lower()

            # TODO: Add support for other file extension
            if CompileEnv.PCH_Act == CompileEnvironment.PCHAction.Create:
                NewArgs = self.ArgPCH()

            # Assume it's C++
            else:
                NewArgs = self.ArgCPP()
                NewArgs += PCH

            for F in CompileEnv.ForceIncFiles:
                NewArgs += ' -include "' + os.path.abspath(F) + '"'

            NewAction.PreconditionItems.append(Item)

            if CompileEnv.PCH_Act == CompileEnvironment.PCHAction.Create:
                InPCH = os.path.join(DirOutput, os.path.abspath(Item) + ".gch")

                CPPOut.PCHFile = InPCH

                NewAction.OutputItems.append(InPCH)

                NewArgs += ' -o "' + os.path.abspath(InPCH) + '"'

            else:

                if CompileEnv.PCH_Act == CompileEnvironment.PCHAction.Include:
                    newAction.PreconditionItems.append(CompileEnv.PCHFile)
                    NewAction.UsingPCH = True

                Obj = os.path.join(DirOutput, os.path.basename(Item) + ".o")

                CPPOut.ObjectFiles.append(Obj)
                NewAction.OutputItems.append(Obj)

                NewArgs += ' -o "' + os.path.abspath(Obj) + '"'

            NewArgs += ' "' + os.path.abspath(Item) + '"'

            if CompileEnv.GenerateDependFile == True:
                DependFile = os.path.join(DirOutput, os.path.basename(Item) + ".d")
                NewArgs += ' -MD -MF "' + os.path.abspath(DependFile) + '"'
                NewAction.OutputItems.append(DependFile)
                NewAction.DependencyListFile = DependFile

            NewAction.CurrentDirectory = Dir_Manager.Engine_Directory

            if self.ClangPath != None and self.ClangPath != "":
                NewAction.CommandPath = self.ClangPath

            elif self.GCCPath != None and self.GCCPath != "":
                NewAction.CommandPath = self.GCCPath
            else:
                Logger.Logger(5, "CLANGPATH AND GCCPATH IS EMPTY OR NONE!")

            AllArgs = Args + NewArgs + CompileEnv.AdditionalArgs

            # FIXME: REPLACE THIS WITH CUSTOM FUNCTION, LET'S JUST CREATE A NEW FILE VIA NORMAL METHOD FOR NOW!

            RespFileName = os.path.join(DirOutput, os.path.basename(Item) + ".rsp")

            Logger.Logger(2, "Creating dir: " + RespFileName)

            os.makedirs(os.path.dirname(RespFileName), exist_ok=True)

            RespFile = open(RespFileName, "w")

            RespFile.write(AllArgs)

            NewAction.PreconditionItems.append(RespFile)

            NewAction.Arguments = '@"' + RespFileName + '"'

            NewAction.UsingGCCCompiler == True

            if CompileEnv.PCH_Act == True:
                if (
                    CompileEnv.PCH_Act == CompileEnvironment.PCHAction.Create
                    or CompileEnv.AllowRemotelyCompiledPCHs == True
                ):
                    CompileAction.CanRunRemotely = True

            OutputActionList.append(NewAction)

        return CPPOut

    def _LinkArgs(self, LinkEnv):
        Ret = ""

        if self.UsingLld(LinkEnv.Arch) == True and LinkEnv.IsBuildingDynamic == False:
            Ret += " -Wl,-fuse-ld=lld"

        Ret += " -rdynamic"

        if LinkEnv.IsBuildingDynamic == True:
            Ret += " -shared"
        else:
            Ret += " -Wl,--unresolved-symbols=ignore-in-shared-libs"

        if self.Option.UseAddressSanitizer == True:
            Ret += " -g -fsanitize=address"

        elif self.Option.UseThreadSanitizer == True:
            Ret += " -g -fsanitize=thread"

        elif self.Option.UseUnknownSanitizer == True:
            Ret += " -g -fsanitize=undefined"

        Ret += " -Wl,-rpath=${ORIGIN} -Wl,-rpath-link=${ORIGIN} -Wl,-rpath=${ORIGIN}/../../bin/Linux"

        Ret += " -Wl,--as-needed -Wl,--hash-style=gnu -Wl,--build-id"

        if self.NotUsingPIE == True and LinkEnv.IsBuildingDynamic == False:
            Ret += " -Wl,-nopie"

        if LinkEnv.PGOOptimize == True:
            Ret += (
                ' -Wno-backend-plugin -fprofile-instr-use="'
                + os.path.join(LinkEnv.PGODirectory, LinkEnv.PGOFilePrefix)
                + '"'
            )

        elif LinkEnv.PGOProfile == True:
            Ret += " -fprofile-generate"

        if LinkEnv.AllowLTCG == True:
            Ret += " -flto"

        if self.IsCrossCompiling == True:

            if self.IsUsingClang == True:

                Ret += " -target " + LinkEnv.Arch

                # Ret += ' "--sysroot=' + BasePath + '"' # FIXME: This breaks my current code, since we are using system shit for now, once I replace those code, re-add this

                Ret += "-B" + BasePath + "/usr/lib/"

                Ret += "-B" + BasePath + "/usr/lib64/"

                Ret += "-L" + BasePath + "/usr/lib/"

                Ret += "-L" + BasePath + "/usr/lib64/"

        return Ret

    def _LinkGroups(self, LinkEnv, OutputResp, OutputAction):

        OutputResp.append(" --start-group")

        ExternalLibs = ""

        for Item in LinkEnv.AdditionalLibs:
            Extension = os.path.splitext(Item)[1]  # Get extension

            if os.path.dirname(Item) == None or os.path.dirname(Item) == "":
                ExternalLibs += " -l" + Item

            elif Extension == ".a":

                Abs = os.path.abspath(Item)

                # Add quotes if there's a space, so that there wouldn't be any errors
                if " " in Abs:
                    Abs = '"' + Abs + '"'

                if LinkEnv.IsBuildingDynamic == True and (
                    "libcrypto" in Abs or "libssl" in Abs
                ):
                    OutputResp.append(" --whole-archive" + Item + " --no-whole-archive")

                else:
                    OutputRest.append(" " + Item)

                AllFiles = File_Manager.GetAllFilesFromDir(Item)
                LinkEnv.PreconditionItems.append(AllFiles)

            else:

                Depend = File_Manager.GetAllFilesFromDir(Item)

                Name = os.path.splitext(Item)[0]

                # removes the lib text if it exists
                if "lib" in Name:
                    Name = Name[:3]

                LibLink = " -l" + Name

                OutputAction.PreconditionItems.append(Depend)
                ExternalLibs += LibLink

        OutputResp.append(" --end-group")

        return ExternalLibs

    # TODO: Add windows support!
    def _STEP1LinkShellFiles(self, LinkEnv, Output, Com, Action):
        LinkName = "link-" + os.path.basename(Output) + ".sh"

        LinkFile = os.path.join(LinkEnv.LocalShadowDir, LinkName)

        Logger.Logger(2, "Creating ShadowDir: " + LinkEnv.LocalShadowDir)

        os.makedirs(LinkEnv.LocalShadowDir, exist_ok=True)

        Logger.Logger(2, "Creating file: " + LinkFile)

        with open(LinkFile, "w") as f:
            Logger.Logger(2, "writing: " + LinkFile)
            f.write("#!/bin/sh\n")
            f.write("set -o errexit\n")
            f.write(Com + "\n")
            # f.write(self.GetEncodeCommand(LinkEnv, Output)) # FIXME: Readd this once we add Breakpad!

        Action.CommandPath = "/bin/sh"
        Action.Arguments = ' "' + LinkFile + '"'

        LinkScriptFile = os.path.join(LinkEnv.LocalShadowDir, "remove-sym.ldscript")

        if os.path.exists(LinkScriptFile):
            Logger.Logger(2, "Removing file: " + LinkScriptFile)
            # os.remove(LinkScriptFile)

    def _STEP2LinkShellFiles(self, LinkEnv, Output, Com, Action, RelinkedFile):
        RelinkName = "Relink-" + os.path.basename(Output) + ".sh"

        RelinkFile = os.path.join(LinkEnv.LocalShadowDir, RelinkName)

        Logger.Logger(2, "Creating dir: " + RelinkFile)

        os.makedirs(RelinkFile, exist_ok=True)

        NewCom = Com

        NewCom = NewCom.replace(Output, RelinkedFile)
        NewCom = NewCom.replace("$", "\\$")

        Logger.Logger(2, "Creating file: " + RelinkFile)

        with open(RelinkFile, "w") as f:
            Logger.Logger(2, "writing: " + RelinkFile)
            f.write("#!/bin/sh\n")
            f.write("set -o errexit\n")
            f.write(Com + "\n")
            f.write("TIMESTAMP='stat --format %y \"" + os.path.abspath(Output) + '"\n')
            f.write("cp " + RelinkFile + " " + os.path.abspath(Output) + "\n")
            f.write(
                "mv "
                + os.path.abspath(Output)
                + ".temp "
                + os.path.abspath(Output)
                + "\n"
            )
            f.write(self.GetEncodeCommand(LinkEnv, Output) + "\n")
            f.write('touch -d "$TIMESTAMP"' + os.path.abspath(Output))

        Action.CommandPath = "/bin/sh"
        Action.Arguments = '"' + RelinkFile + '"'

    def LinkFiles(self, LinkEnv, ImportLibraryOnly, OutputActionList):

        if (
            LinkEnv.AllowLTCG == True
            or LinkEnv.PGOProfile == True
            or LinkEnv.PGOOptimize
        ) and CanAdvanceFeatures(LinkEnv.Arch) == False:
            Logger.Logger(
                5,
                "FATAL: AllowLTCG, PGOProfile, and/or PGOOptimize is true, but we cannot use advance features!",
            )

        if LinkEnv.IsBuildingLibrary == True or ImportLibraryOnly == True:
            return ArchiveAndIndex(LinkEnv, OutputActionList)

        RPath = []

        NewAction = Action.Action()

        NewAction.CurrentDirectory = Dir_Manager.Engine_Directory

        Com = ""

        if self.ClangPath != None and self.ClangPath != "":
            Com += '"' + self.ClangPath + '"'

        else:
            Com += '"' + self.GCCPath + '"'

        Com += self._LinkArgs(LinkEnv)

        NewAction.CreateImportLib = LinkEnv.IsBuildingDynamic

        Output = LinkEnv.OutputPaths[0]

        NewAction.OutputItems.append(Output)

        # TODO: Add description debugging support

        Com += " -o " + os.path.abspath(Output)

        Resp = []

        for Item in LinkEnv.InputFiles:

            Resp.append(os.path.abspath(Item))
            NewAction.PreconditionItems.append(Item)

        if LinkEnv.IsBuildingDynamic == True:
            Resp.append(" -soname=" + Output)

        AllLib = LinkEnv.LibraryPaths  # All libs combined

        for Item in LinkEnv.AdditionalLibs:

            ItemPath = os.path.dirname(Item)

            # If Item contains Plugin or ThirdParty, and is not the absolute file
            if ("Plugin" in Item or "bin/ThirdParty" in Item) and os.path.dirname(
                Item
            ) != os.path.abspath(Output):

                Relative = os.path.relpath(Item, os.path.dirname(Output))

                if (
                    IsCrossCompiling() == True
                    and Dir_Manager.Engine_Directory in Relative
                ):
                    Temp = Relative.replace(Dir_Manager.Engine_Directory, "")

                    # If we are on Linux Root Directory, we just need to move back the directory, otherwise we will include Temp
                    Relative = "../../../"
                    if not Temp.startswith("/"):
                        Relative += Temp

                if Relative not in RPath:
                    RPath.append(Relative)
                    Resp.append(' -rpath=$"{{ORIGIN}}' + Relative + '"')

        for Item in LinkEnv.RuntimeLibPaths:

            # Temp var so we can modify it if needed
            ItemTemp = Item

            if not ItemTemp.startswith("$"):
                RootPath = os.path.relpath(ItemTemp, Dir_Manager.Engine_Directory)
                ItemTemp = os.path.join("..", "..", "..", RootPath)

            if ItemTemp not in RPath:
                RPath.append(ItemTemp)
                Resp.append(' -rpath="${{ORIGIN}}' + ItemTemp + '"')

        Resp.append(' -rpath-link="' + os.path.dirname(Output) + '"')

        for Item in AllLib:
            Resp.append(' -L"' + Item + '"')

        ExternalLibs = self._LinkGroups(LinkEnv, Resp, NewAction)

        RespFile = self.GetResponseName(LinkEnv, Output)

        File_Manager.CreateIntermedFile(RespFile, Resp)

        Com += ' -Wl,@"' + RespFile + '"'

        NewAction.PreconditionItems.append(RespFile)

        Com += " -Wl,--start-group" + ExternalLibs + " -Wl,--end-group -lrt -lm"

        # FIXME: Add libCXX support

        if self.SDK.VerboseLinker == True:
            Com += " -Wl,--verbose -Wl,--trace -v"

        Com += LinkEnv.AdditionalArgs

        # Fix bugs if we accidently use windows shit
        Com = Com.replace("{", "'{")
        Com = Com.replace("}", "}'")
        Com = Com.replace("$'{", "'${")

        self._STEP1LinkShellFiles(LinkEnv, Output, Com, NewAction)

        OutputActionList.append(NewAction)

        if LinkEnv.IsBuildingDynamic == True:
            # -- Start Relink -- #

            RelinkAction = Action.Action()

            RelinkAction.CurrentDirectory = NewAction.CurrentDirectory

            RelinkAction.OutputItems.append(Output)

            RelinkedFile = os.path.join(LinkEnv.LocalShadowDir, OutputFile + ".Relink")

            Dummmy = os.path.join(
                LinkEnv.LocalShadowDir, OutputFile + ".Relink_Action_Ran"
            )

            RelinkAction.OutputItems.append(Dummy)

            _STEP2LinkShellFiles(LinkEnv, Output, Com, RelinkAction, RelinkedFile)

            OutputActionList.append(RelinkAction)

        return Output

    def PostBuilt(File, LinkEnv, ActionList):
        Output = super().PostBuilt(File, LinkEnv, ActionList)

        if LinkEnv.IsBuildingDynamic == True and LinkEnv.CrossedReference == True:
            RelinkMap = os.path.join(
                LinkEnv.LocalShadowDir, OutputFile + ".Relink_Action_Ran"
            )
            Output.append(RelinkMap)

        return Output

    @staticmethod
    def Print(CompileEnv):
        return ""
