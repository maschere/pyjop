__pdoc__ = {}
__pdoc__["EntityBase.NPArray"] = False
__pdoc__["Network.SockAPIClient"] = False

__a = set(dir())

import builtins
from pyjop.EntityBase import _is_custom_level_runner, _internal_python_process
builtins.print("Initializing JOY OF PROGRAMMING Python process.", end="")
del builtins
from pyjop.Enums import *
import builtins
builtins.print(".", end="")
del builtins
from pyjop.EntityBase import *
import builtins
builtins.print(".", end="")
del builtins
from pyjop.EntityClasses import *
import builtins
builtins.print(".", end="")
del builtins
from pyjop.Network import *
import builtins
builtins.print(".", end="")
del builtins
from pyjop.Vector import Vector3
import builtins
builtins.print(".", end="")
del builtins

__b = set(dir()).difference(__a)
del __a

for __x in __b:
    if __x in globals():
        del globals()[__x]

del __b

# audit hook
import inspect
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module
import importlib.metadata
PYJOP_VERSION = importlib.metadata.version('pyjop')
import builtins
builtins.print(".", end="")
del builtins

# iterate through the modules in the current package
__package_dir = Path(__file__).resolve().parent
for _, __module_name_it, _ in iter_modules([__package_dir]):
    # import the module and iterate through its attributes
    __moduleit = import_module(f"{__name__}.{__module_name_it}")
    for __attribute_name_it in dir(__moduleit):
        __attribute_it = getattr(__moduleit, __attribute_name_it)

        if (
            inspect.isclass(__attribute_it) or inspect.isfunction(__attribute_it)
        ) and inspect.getmodule(__attribute_it).__package__ == "pyjop":
            # Add the class to this package's variables
            globals()[__attribute_name_it] = __attribute_it

import builtins
builtins.print(".", end="")
del builtins
# clean up
del (
    inspect,
    iter_modules,
    Path,
    import_module,
    __package_dir,
    __module_name_it,
    __moduleit,
    __attribute_it,
    __attribute_name_it,
)
import builtins
builtins.print(" DONE")
del builtins

from sys import addaudithook
# import importlib.util
from os import path
# import re
#_mypath = str(path.normpath(__file__)).replace("\\","/").split("/000_MyContent/External/")[0]
def _sandbox_editor(event,arg):
    if type(event) != str: raise
    if event=='open':
        if len(arg)>1 and arg[1] and arg[1]!='r' and arg[1]!='rb' and type(arg[0]) is not int:
            if not (type(arg[0]) is str and arg[0].endswith(".matplotlib-lock")):
                #print(event, arg)
                raise PermissionError("Writing files forbidden.")

    if event == "socket.bind":
        if arg[1][0] != "127.0.0.1":
            #print(event, arg)
            raise PermissionError("Socket binding not allowed")
    if event == "socket.connect" and not (len(arg)>1 and len(arg[1])>1 and arg[1][0] == "127.0.0.1"):
        #print(event, arg)
        raise PermissionError("Network connections not allowed")
    if event.split('.')[0] in ['subprocess', 'shutil', 'ftplib']: 
        #print(event, arg)
        raise PermissionError('potentially dangerous, subprocess, shutil, forbidden'  + str(event))
    if event.split('.')[0] == "winreg":
        cmd = event.split('.')[1]
        if cmd not in ["ConnectRegistry", "LoadKey", "OpenKey", "OpenKey/result", "QueryValue", "QueryInfoKey", "EnumKey", "EnumValue"]:
            #print(event, arg)
            raise PermissionError('potentially dangerous, winreg forbidden'  + str(event))
    if event.split('.')[0] == "os" and event.split('.')[1] not in ["listdir", "scandir", "add_dll_directory", "putenv", "walk", "unsetenv","mkdir"]:
        #print(event, arg)
        if not (event == "os.remove" and arg[0].endswith(".matplotlib-lock")):
            raise PermissionError('potentially dangerous, os access forbidden: ' + str(event))
    # if event == "compile":
    #     raise PermissionError('potentially dangerous, compile and exec forbidden')
    # if event == "exec":
    #     p = str(path.normpath(arg[0].co_filename)).replace("\\","/")
    #     if "/000_MyContent/External/python-3.10.4-embed-amd64/python310.zip/" not in p and "/000_MyContent/External/python-3.10.4-embed-amd64/Lib/site-packages/" not in p:
    #         raise PermissionError('potentially dangerous, compile and exec forbidden' + str(arg))
    # if event == "import":
    # #     # spec = importlib.util.find_spec(arg[0])
    # #     # p = str(path.normpath(spec.origin)).replace("\\","/")
    # #     # #if p.startswith(__file__)
        
    # #     # if p.startswith(_mypath + "/000_MyContent/External/python-3.10.4-embed-amd64/") == False:
    #     raise PermissionError('Custom imports forbidden.')
if _is_custom_level_runner() or _internal_python_process():        
    addaudithook(_sandbox_editor)
del addaudithook