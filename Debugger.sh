# DEBUGGER

# Uses flake8 to check for errors in the code, stores them in thingstofix.txt

# F841 ignored since many "unused" variables are actually used in other files, such as CompileEnv, ModuleReader, etc

# F401 will be ignored for now but will remove later once we are in the cleanup code phase (no, using projectCleaner.py doesn't count!)

# W503 is a new standard feature that Black doesn't support yet, you may remove this once Black supports this warning fix\

# E501 annoying line too long error, thought Black fixes this? Please re-run

# W391 blank line doesn't do shit I think

flake8 --ignore=F841,F401,W503,E501,W391 > thingstofix.txt 2>&1
