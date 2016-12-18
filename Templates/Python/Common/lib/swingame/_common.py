from __future__ import print_function
from ctypes import cdll, CDLL, c_int, c_char_p, create_string_buffer

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
    if result_buffers == 0:
        return f
    # returning string[s]
    assert ret_type is None
    from functools import wraps
    @wraps(f)
    def wrapper(*args):
        bufs = tuple(create_string_buffer(_BUFLEN) for _ in range(result_buffers))
        f(*(args + bufs))
        return tuple(b.value for b in bufs)
    wrapper.__func__ = f
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
