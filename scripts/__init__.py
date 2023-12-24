from os.path import isfile, join, dirname, abspath
from os import listdir


res = dirname(abspath(__file__))
only_files = [f[:f.rfind('.')] for f in listdir(res) if isfile(join(res, f))][:-1]

__all__ = []
modules = set()
for module_name in only_files:
    temp_module = __import__("scripts."+module_name)
    modules.add(temp_module)
    __all__.append(module_name)
