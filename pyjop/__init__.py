__pdoc__ = {}
__pdoc__["EntityBase.NPArray"] = False
__pdoc__["Network.SockAPIClient"] = False

__a = set(dir())

from pyjop.Enums import *
from pyjop.EntityBase import *
from pyjop.EntityClasses import *
from pyjop.Network import *

__b = set(dir()).difference(__a)
del __a

for __x in __b:
    if __x in globals():
        del globals()[__x]

del __b

#audit hook
import inspect
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module


# iterate through the modules in the current package
__package_dir = Path(__file__).resolve().parent
for (_, __module_name_it, _) in iter_modules([__package_dir]):
    # import the module and iterate through its attributes
    __moduleit = import_module(f"{__name__}.{__module_name_it}")
    for __attribute_name_it in dir(__moduleit):
        __attribute_it = getattr(__moduleit, __attribute_name_it)
        
        if (inspect.isclass(__attribute_it) or inspect.isfunction(__attribute_it)) and inspect.getmodule(__attribute_it).__package__=="pyjop":     
            # Add the class to this package's variables
            globals()[__attribute_name_it] = __attribute_it



#clean up
del inspect,iter_modules,Path,import_module,__package_dir,__module_name_it,__moduleit,__attribute_it,__attribute_name_it

