import importlib
import os
import re
import subprocess

import LinuxPlatformSDK
import Common

sys.path.append("../../Template")

import Toolchain

sys.path.append("../../Internal")

import CompileEnvironment

import Action

sys.path.append("../../Configuration")

import Directory_Manager as Dir_Manager

class Options:

    UseAddressSanitizer = False

    UseThreadSanitizer = False

    UseUnknownSanitizer = False

    def IsNone(self):
        if self.UseAddressSanitizer == False and self.UseThreadSanitizer == False and UseUnknownSanitizer == False:
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

    #Cashe variables
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

    # If we already used LLD
    _LldUsed = False

    _HostOS = platform.system()

    SDK = LinuxPlatformSDK.LinuxPlatformSDK

    Option = Options

    def __init__(self, InArch, InSDK, InSavePYSM=False, InOptions=None, InPlatform=None):

        # If InPlatform is none, we will use Linux, otherwise we will use InPlatform
        if InPlatform == None:
            self._RunBase(InArch, InSDK, CompileEnvironment.Platform.Linux, InSavePYSM, InOptions)
        else:
            self._RunBase(InArch, InSDK, InPlatform, InSavePYSM, InOptions)


        MultiArchRoot = SDK.GetSDKLoc()
        BasePath = SDK.GetSDKArchPath()

        CanUseSystemCompiler = SDK.CanUseSystemCompiler()
        IsCompilerValid = False

        if CanUseSystemCompiler == False and (BasePath == None or BasePath == ""):
            raise ValueError("ERROR: LINUX_ROOT environment variable is not set!")

        DumpSymsPath = os.path.join(Dir_Manager.Engine_Directory, "bin", "Linux", "DumpSyms")
        BreakpadEncoderPath = os.path.join(Dir_Manager.Engine_Directory, "bin", "Linux", "BreakpadEncoder")

        if (BasePath != None or BasePath != "") and (MultiArchRoot == None or MultiArchRoot == ""):
            MultiArchRoot = BasePath

        # Validate the Compiler if we are using a system, but the compiler isn't valid
        if CanUseSystemCompiler == True and IsCompilerValid == False:
            ClangPath = os.path.join(BasePath, "bin", "clang++")
            GCCPath = Common.WhichGCC(BasePath, "bin", "g++")
            ArPath = Common.WhichAR(BasePath, "bin", Arch + "-ar")
            llvmArPath = Common.WhichLLVM(BasePath, "bin", "llvm-ar")
            RanLibPath = Common.WhichRanLib(BasePath, "bin", Arch + "-ranlib")
            StripPath = Common.WhichStrip(BasePath, "bin", Arch + "-strip")
            ObjectCopyPath = Common.WhichObjCopy(BasePath, "bin", Arch + "objcopy")

            # FixDepends supports only on windows
            if _HostOS == "Windows":
                UseFixedDepends = True

            # if the currently running OS is Linux, we will ensure all lang types are overwritten by POSIX ASCII only system
            if _HostOS == "Linux":
                os.environ["LC_ALL"] = "C"

            # These settings allow us to cross compile
            IsCrossCompiling == True

            #FIXME: Make sure this is accuate once we add it!
            IsCompilerValid = GetCompilerVersion()


        # Validate system Toolchain
        _ValidateSystemToolchain()


        # Check the compiler settings
        CheckDefaultCompilerSettings()

        #TODO: Add proper detection
        _LldUsed = True


    # Validate system Toolchain
    def _ValidateSystemToolchain():
        if CanUseSystemCompiler == True and IsCompilerValid == False:
            ClangPath = Common.WhichClang()
            GCCPath = Common.WhichGCC()
            ArPath = Common.WhichAR()
            llvmArPath = Common.WhichLLVM()
            RanLibPath = Common.WhichRanLib()
            StripPath = Common.WhichStrip()
            ObjectCopyPath = Common.WhichObjCopy()

            UseFixedDepends = False

            # These settings allow us to cross compile
            IsCrossCompiling == False

            #FIXME: Make sure this is accuate once we add it!
            IsCompilerValid = GetCompilerVersion()


    # Run's the parent init and set some values
    def _RunBase(self, InArch, InSDK, InPlatform, InSavePYSM=False, InOptions=None):
        super().__init__(InPlatform)
        Arch = InArch
        SavePYSM = InSavePYSM
        Option = InOptions


    # Return's if Toolchain supports Cross Compiling
    def CrossCompiling():
        return IsCrossCompiling

    # Return's true if we are using clang
    def IsUsingClang():
        if ClangPath is not None and ClangPath != "":
            return True
        return False

    # Set the array version from string
    def SetVersionArray():
        VersionArrayString = Version.split(".")

        tmp = 0

        while tmp < len(VersionArrayString) - 1:
            Version[tmp] = int(VersionArrayString[tmp])
            tmp += 1


    def GetEncodeCommand(LinkEnv, OutputFile):
        # FIXME: Add Windows Support!

        OutputFileFullLoc = os.path.abspath(OutputFile) # Get full file path

        OutputFileWithoutExt = os.path.splitext(OutputFileFullLoc)[0] # Removes the extension

        EncodeSymbolFile = os.path.join(LinkEnv.OutputDir, OutputFileWithoutExt + ".sym")

        SymbolFile = os.path.join(LinkEnv.LocalShadowDir, OutputFile + ".pysm")

        StripFile = os.path.join(LinkEnv.LocalShadowDir, OutputFile + "_nodebug")

        DebugFile = os.path.join(LinkEnv.OutputDir, OutputFileWithoutExt + ".debug")

        # If SavePYSM is true, then we will store the symbol file in the output directory instead of the shadow directory
        if SavePYSM == True:
            SymbolFile = os.path.join(LinkEnv.OutputDir, OutputFileWithoutExt + ".pysm")


        # Compile dump_syms
        Ret = '"' + DumpSymsPath + '" -c -o "' + OutputFileFullLoc + '" "' + os.path.abspath(SymbolFile) + '"\n'

        #encode breakpad symbols
        Ret += '"' + BreakpadEncoderPath + '" "' + os.path.abspath(SymbolFile) + '" "' + os.path.abspath(EncodeSymbolFile) + '" \n'


        # Write debug information
        if LinkEnv.AddDebugInfo == True:

            # use objcopy on strip file
            Ret += '"' + ObjectCopyPath + '" --strip-all "' + os.path.abspath(OutputFile) + '" "' + os.path.abspath(StripFile) + '"\n'


            # use objcopy on debug file
            Ret += '"' + ObjectCopyPath + '" --only-keep-debug "' + os.path.abspath(OutputFile) + '" "' + os.path.abspath(DebugFile) + '"\n'


            # use objcopy to link Debug file to the Final .so file, using temp to avoid corruption
            Ret += '"' + ObjectCopyPath + '" --add-gnu-debuglink="' + os.path.abspath(DebugFile) + '" "' + os.path.abspath(StripFile) + '" "' + os.path.abspath(OutputFile) + '.temp" \n'


            # Rename the .temp to the final name

            Ret += 'mv "' + os.path.abspath(OutputFile) + '.temp" "' + os.path.abspath(OutputFile) + '"\n'

            # Change permission to normal (this permission allows main user to read and write, but other users can only read it)
            Ret += 'chmod 644 "' + os.path.abspath(DebugFile) + '"\n'

        else:

            Ret += '"' StripFile + '" "' + os.path.abspath(OutputFile) + '"'

        return Ret


    def GetCompilerVersion():
        # Check Clang
        if ClangPath != "":
            App = subprocess.run([ClangPath, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

            Out = App.stdout

            Match = re.search(r"clang version (\d+\.\d+(\.\d+)?)", Out)

            if Match:
                VersionString = Match.group(1)


    def SetDefaultCompilerSettings():
        if ClangPath != "":

            App = subprocess.run([ClangPath, "-E", "-dM", "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

            for Line in App.stdout:
                LineStrip = Line.strip()

                if LineStrip == None or LineStrip == "":
                    break

                if "__pie__" in LineStrip or "__PIE__" in LineStrip:
                    NotUsingPIE = True

    # Set switches depending on architecture
    def ArchSwitch(Arch):
        if Arch.startswith("arm") or Arch.startswith("aarch64"):
            return " -fsigned-char" # Tells the compiler to treat char as signed chars
        return ""

    # Set defines based on the architecture
    def ArchDefine(Arch):
        if Arch.startswith("x86_64") or Arch.startswith("aarch64"):
            return " -D_LINUX64"
        return ""



    def UseLibCXX(Arch):
        Override = os.environ["RBT_Use_LibCXX"]

        # If Override is valid
        if Override == None or Override == "":

            # If Override is true
            if Override == "True" or Override == "true" or Override == "1":

                # If Override starts with supported arch, return true
                if Override.startswith("i686") or Override.startswith("x86_64") or Override.startswith("aarch64"):
                    return True

        return False


    # Fix the args to make it compatable
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

            Value.replace('\"', "\\\"")

        if Value == None:
            return Key
        else:
            return Key + "=" + Value



    def ArgCPP():
        return " -x c++ -std=c++14"


    def ArgPCH():
        return " -x c++-header -std=c++14"

    # Whether to use llvm-ar or ar
    #TODO: Temp solution, assumes it's system-wide, add support for non-system wide
    def ArchiveProgram():
        if LlvmArPath != "":
            return "llvm-ar"
        elif ArPath != "":
            return "ar"
        else:
            raise ValueError("Cannot create llvm-ar or ar. Both tools cannot be found")


    def ArgArchive():
        return " rcs"


    def CanAdvanceFeatures():
        if UsingLld == True:
            if LlvmArPath != None and LlvmArPath != "":
                return True
        return False


    def SDKVersionCorrect():
        pass


    def UsingLld(Arch):
        if _LldUsed == True and Arch.startswith("x86_64"):
            return True
        return False


    def GetResponseName(LinkEnv, OutputFile):
        os.path.join(LinkEnv.IntermediateDir, os.path.basename(OutputFile) + ".response")


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


        ResponsePath = GetResponseName(LinkEnv, OutputFile)

        #FIXME: Add support for not generating project files support (Requires class that doesn't exist yet) This will create intermediate file and add it to precondition list

        if LlvmArPath == None or LlvmArPath == "":
            Archive.Arguments += ' && "' + self.RanlibPath + '" "' + os.path.abspath(OutputFile) + '"'

        Archive.Arguments += " " + LinkEnv.AdditionalArgs

        Archive.Arguments += "'"

        OutputActionList.append(Archive)

        return OutputFile



    def GetGlobalArg(CompileEnv):
        pass


    def CompileFiles(CompileEnv, InputFilesList, DirOutput, Name, OutputActionList):
        pass


    def LinkFiles(LinkEnv, ImportLibraryOnly, OutputActionList):
        pass


    def PostBuilt(File, LinkEnv, ActionList):
        pass


    def Print():
        pass
