import configparser

def ReadConfig(File, Class, Value):
    Config = configparser.ConfigParser()

    try:
        Config.read(File)
    except:
        raise ValueError("Error, unable to read and parse config file: " + str(File))

    try:
        Ret = Config.get(Class, Value)
    except:
        raise ValueError("Error, unable to read value (CLASS: " + str(Class) + ", VALUE: " + str(Value))
    return Ret
