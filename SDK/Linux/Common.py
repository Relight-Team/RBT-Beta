import os
import subprocess

def Which(Name):

    args = ["/bin/sh",  "-c 'which " + Name + "'"]

    RunningProgram = subprocess.Popen(args, stdout=subprocess.PIPE)

    stdout = RunningProgram.communicate

    if RunningProgram.returncode == 0:
        return stdout.decode()
    return None

def WhichClang():
    return Which("Clang++")

def WhichGCC():
    return Which("g++")

def WhichAR():
    return Which("ar")

def WhichLLVM():
    return Which("llvm-ar")

def WhichRanLib():
    return Which("ranLib")

def WhichStrip():
    return Which("strip")

def WhichObjCopy():
    return Which("objcopy")
