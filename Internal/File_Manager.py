import os
from . import Logger


def GetAllFilesFromDir(Path):

    if os.path.isdir(Path):
        return os.listdir(Path)


def CreateIntermedFile(Path, Content):

    Logger.Logger(2, "Creating Intermediate file at " + Path)

    Dir_Name = os.path.dirname(Path)

    os.makedirs(Dir_Name, exist_ok=True)

    # File doesn't exist, nothing to back up
    if not os.path.exists(Path):
        Fil = open(Path, "w")
        NewWrite = str("".join(Content))
        Fil.write(NewWrite)
        Fil.close()

    # Backup old data
    else:

        BackupFile = Path + ".backup"
        # TODO: Add windows support
        Logger.Logger(
            2,
            "Creating backup of "
            + Path
            + " called "
            + BackupFile
            + ". Writing to initial path now",
        )
        os.system("mv " + Path + " " + BackupFile)

        Fil = open(Path, "w")
        NewWrite = str("".join(Content))
        Fil.write(NewWrite)
        Fil.close()
