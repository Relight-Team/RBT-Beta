import inspect
import os

def Test():

    frame        = inspect.currentframe()          # <frame at ...>
    caller       = frame.f_back
    func_name    = caller.f_code.co_name            # current function
    file_path    = caller.f_code.co_filename        # absolute path to this file
    file_name    = os.path.basename(file_path)     # just the file (not the path)

    Func = caller.f_code.co_name


    stack = inspect.stack()
    # The caller's frame is at index 1 in the stack
    caller_frame = stack[1]

    if 'self' in caller_frame.frame.f_locals:
        caller_instance = caller_frame.frame.f_locals['self']
        cls_name = caller_instance.__class__.__name__
    else:
        cls_name = None

    if cls_name == None:
        cls_name = "None"




    print("Currently running file: should be B.py: " + file_name)
    print("Currently running function: should be Temp() " + Func)
    print("Currently running class: should be Test " + cls_name)
