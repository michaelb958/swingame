from . import _common, graphics
from .sgsdk import *

def _guess_app_path():
    from sys import argv
    import os
    tried = []
    for p_base in (os.path.dirname(argv[0]), os.getcwd()):
        for i in range(3):
            p = os.path.join(p_base, *(i * ['..'] + ['Resources']))
            tried.append(p)
            if os.path.isdir(p):
                set_app_path(p)
                return
    else:
        raise RuntimeError('Resources directory not found: tried ' + '; '.join(tried))
_guess_app_path()

Color = type('Color', (_common.c_int_enum,),
    {k[6:]: v() for k, v in graphics.__dict__.items()
                if k.startswith('color_')
                and len(v.argtypes) == 0})

__all__ = [g for g in list(globals()) if g != 'graphics'
                                      and not g.startswith('_')
                                      and g not in dir(_common)]
