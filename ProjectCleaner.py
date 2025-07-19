import os

# This file will clean up your code, so you can focus on actually making shit instead of worrying about format :)

# REQUIRES:

# BLACK (python)

for Dir, _, Files in os.walk(os.getcwd()):
    for Item in Files:
        if Item.endswith(".py"):
            os.system("black " + os.path.join(Dir, Item))
