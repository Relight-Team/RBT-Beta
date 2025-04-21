import ConfigManager as CM

def GetValue(Val):
    return CM.ReadConfig("../../../Configs/BaseBuilder.cfg", "LogInformation", Value)

def IsTrue(Val):
    if GetValue(Val) == "true":
        return True
    else:
        return False

class Logger:

    def CoreLogger(Str):
        if IsTrue("CoreLogger") == True:
            print(Str)

    def BaseLogger(Str):
        if IsTrue("BaseLogger") == True:
            print(Str)

    def HighLogger(Str):
        if IsTrue("HighLogger") == True:
            print(Str)

    def LogWarning(Str):
        if IsTrue("LogWarning") == True:
            print("Warning: " + Str)
