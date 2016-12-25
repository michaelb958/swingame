from __future__ import print_function
from ctypes import cdll, c_int, c_char_p, create_string_buffer
from functools import wraps

_BUFLEN = 256

# need this to find SGSDK.dll in the app's directory
from sys import argv
from os.path import abspath, dirname
try:
    unicode
except NameError:
    unicode = str
try:
    cdll.kernel32.SetDllDirectoryW(unicode(dirname(abspath(argv[0]))))
except AttributeError:
    # not on Windows
    pass

SGSDK = cdll.SGSDK

def extern(f, argtypes, doc=None, ret_type=c_int, result_buffers=0):
    if doc is not None:
        f.__doc__ = doc
    f.restype = ret_type
    f.argtypes = argtypes + [c_char_p] * result_buffers
    str_indices = [idx for idx, i in enumerate(argtypes) if i is c_char_p]
    @wraps(f)
    def wrapper(*args):
        args = tuple(a.encode() if i in str_indices else a for i, a in enumerate(args))
        if result_buffers:
            bufs = tuple(create_string_buffer(_BUFLEN) for _ in range(result_buffers))
            f(*(args + bufs))
            results = tuple(b.value.decode() for b in bufs)
            return results[0] if len(results) == 1 else results
        else:
            return f(*args)
    wrapper.argtypes = f.argtypes
    return wrapper

class c_int_enum_META(type):
    @staticmethod
    def transform(n):
        return c_int(n) if isinstance(n, int) else n
    
    def __new__(cls, name, bases, ns):
        return type.__new__(cls, name, bases, {k: cls.transform(v) for k, v in ns.items()})
    def __setattr__(self, key, value):
        type.__setattr__(self, key, type(self).transform(value))

# Py2-Py3 compat hackery
def from_metaclass(metacls):
    return metacls('from_metaclass(%s)' % metacls.__name__, (object,), {})

class c_int_enum(from_metaclass(c_int_enum_META)):
    def __new__(cls, *args):
        raise RuntimeError("can't instantiate an enum")
    
    # needed for ctypes to play nice
    @classmethod
    def from_param(self):
        pass
