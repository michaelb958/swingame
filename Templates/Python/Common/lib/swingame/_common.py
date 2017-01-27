from __future__ import print_function
from ctypes import cdll, c_int, c_bool, c_char_p, create_string_buffer
from ctypes.util import find_library
from functools import wraps

_BUFLEN = 512

# need this to find SGSDK.dll in the app's directory on Windows
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

try:
    SGSDK = cdll.SGSDK
except AttributeError:
    SGSDK = find_library('SGSDK')
    if SGSDK is None:
        raise ImportError("can't find SGSDK library")

class SwinGameError(Exception):
    pass

SGSDK.sg_Utils_ExceptionOccured.argtypes = []
SGSDK.sg_Utils_ExceptionOccured.restype = c_bool
del SGSDK.sg_Utils_ExceptionOccured.errcheck

SGSDK.sg_Utils_ExceptionMessage.argtypes = [c_char_p]
SGSDK.sg_Utils_ExceptionMessage.restype = None
del SGSDK.sg_Utils_ExceptionMessage.errcheck

def sg_errcheck(result, func, args):
    if SGSDK.sg_Utils_ExceptionOccured():
        msg = create_string_buffer(_BUFLEN)
        SGSDK.sg_Utils_ExceptionMessage(msg)
        raise SwinGameError('{0}({1}): {2}'.format(func.__name__, ', '.join(map(repr, args)), msg.value.decode()))
    else:
        return result

def extern(f, argtypes, doc=None, ret_type=c_int, result_buffers=0):
    if doc is not None:
        f.__doc__ = doc
    f.restype = ret_type
    f.argtypes = argtypes + [c_char_p] * result_buffers
    f.errcheck = sg_errcheck
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
    wrapper.argtypes = argtypes
    return wrapper

class c_int_enum_META(type):
    @staticmethod
    def transform(n):
        return c_int(n) if isinstance(n, int) else n
    
    def __new__(cls, name, bases, ns):
        return type.__new__(cls, name, bases, {k: cls.transform(v) for k, v in ns.items()})
    def __setattr__(self, key, value):
        super(c_int_enum_META, self).__setattr__(key, type(self).transform(value))
    
    def __iter__(self):
        items = [(k, v) for k, v in self.__dict__.items() if isinstance(v, c_int)]
        items.sort(key=lambda i: i[0])
        return iter(items)

# Py2-Py3 compat hackery
def from_metaclass(metacls):
    return metacls('from_metaclass(%s)' % metacls.__name__, (object,), {})

class c_int_enum(from_metaclass(c_int_enum_META), c_int):
    def __new__(cls, value):
        for v in cls.__dict__.values():
            if v.value == value:
                return v
        else:
            raise ValueError('value not present in enum')
    
    # needed for ctypes to play nice
    @classmethod
    def from_param(self):
        pass
