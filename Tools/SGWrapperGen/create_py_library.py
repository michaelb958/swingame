#!/usr/bin/env python
# encoding: utf-8
"""
create_py_lib.py

Created by Clinton Woodward on 2009-07-09.
Copyright (c) 2009. All rights reserved.

# stage 1: a simple ctypes binding wrapper for the sgsdk.dll methods
# stage 2: a compile python module to call sgsdk.dll using cython (~pyrex)

swingame/     - the module name
  __init__.py - pulls in other modules as needed (for SwinGame)
  core.py     - core application (gameloop) methods
  audio.py    - music sound ...
  physics.py  - collisions ...
  ...
  sgsdk.py - contains the mapping of all functions

"""

from __future__ import print_function

import logging
import sys
import os
import os.path

from sg import parser_runner
from sg.sg_cache import logger, find_or_add_file
from sg.print_writer import PrintWriter
from sg.file_writer import FileWriter
from sg.sg_type import SGType
from sg.sg_parameter import SGParameter

import py_lib # template definitions

import generated_folders

_out_path = os.path.join('..', '..', 'Generated', 'Python', 'lib', 'swingame')
try:
    os.makedirs(_out_path)
except OSError:
    pass

_procedure_lines = None
_function_lines = None
_exports_header = ''

# POST-PROCESSING - used in wrapped method bodies
_data_switcher = {
    # Pascal type -> what values of this type switch to
    # %s = data value
    'Boolean': 'bool(%s)',
    'LongBool': '(1 if bool(%s) else 0)',
}
# literal substitution
_adapter_type_switcher = {
    'void': None,
    'animation': 'Animation',
    'animationscript': 'AnimationScript',
    'arduinodevice': 'ArduinoDevice',
    'bitmap': 'Bitmap',
    'bitmap[0..n - 1]': 'POINTER(Bitmap)',
    'bitmapptr': 'POINTER(Bitmap)',
    'boolean': 'c_bool',
    'boolean[0..n - 1]': 'POINTER(c_bool)',
    'boolean[0..n - 1][0..n - 1]': 'POINTER(c_bool)',
    'byte': 'c_byte',
    'circle': 'Circle',
    'collisionside': 'CollisionSide',
    'color': 'c_uint32',
    'connection': 'Connection',
    'drawingdest': 'DrawingDest',
    'font': 'Font',
    'fontalignment': 'FontAlignment',
    'fontstyle': 'FontStyle',
    'freenotifier': 'CFUNCTYPE(None, c_void_p)',
    'guieventcallback': 'CFUNCTYPE(None, Region, EventKind)',
    'httpresponse': 'HttpResponse',
    'keycode': 'KeyCode',
    'linesarray': 'LinesArray',
    'linesegment': 'LineSegment',
    'linesegmentptr': 'POINTER(LineSegment)',
    'longbool': 'c_int',
    'longint': 'c_int',
    'longint[0..n - 1]': 'POINTER(c_int)',
    'longint[0..n - 1][0..n - 1]': 'POINTER(c_int)',
    'longintarray': 'POINTER(c_int)',
    'longintptr': 'POINTER(c_int)',
    'longword': 'c_uint32',
    'map': 'MapRecord',
    'mapanimationdata[0..n - 1]': 'POINTER(MapAnimationData)',
    'mapcollisiondata': 'MapCollisionData',
    'mapdata': 'MapData',
    'maplayerdata[0..n - 1]': 'POINTER(MapLayerData)',
    'maptag': 'c_int',
    'maptagdetails[0..n - 1][0..23]': 'POINTER(MapTagDetails)',
    'maptile': 'MapTile',
    'matrix2d': 'Matrix2D',
    'message': 'Message',
    'mousebutton': 'MouseButton',
    'music': 'Music',
    'panel': 'Panel',
    'point2d': 'Point2D',
    'point2d[0..2]': 'POINTER(Point2D)',
    'point2d[0..3]': 'POINTER(Point2D)',
    'point2d[0..n - 1]': 'POINTER(Point2D)',
    'point2darray': 'POINTER(Point2D)',
    'point2dptr': 'POINTER(Point2D)',
    'pointer': 'c_void_p',
    'psdl_surface': 'c_void_p',
    'rectangle': 'Rectangle',
    'region': 'Region',
    'resourcekind': 'ResourceKind',
    'serversocket': 'ServerSocket',
    'single': 'c_float',
    'single[0..2][0..2]': 'POINTER(c_float)',
    'singleptr': 'POINTER(c_float)',
    'soundeffect': 'SoundEffect',
    'sprite': 'Sprite',
    'spriteendingaction': 'c_int',
    'spriteeventhandler': 'CFUNCTYPE(None, Sprite, SpriteEventKind)',
    'spritefunction': 'CFUNCTYPE(None, Sprite)',
    'spritekind': 'c_int',
    'spritesinglefunction': 'CFUNCTYPE(None, Sprite, c_float)',
    'string': 'c_char_p',
    'timer': 'Timer',
    'triangle': 'Triangle',
    'uint16': 'c_uint16',
    'vector': 'Vector',
    'window': 'Window',
    'word': 'c_uint16'
}


def arg_visitor(arg_str, the_arg, for_param_or_type):
    '''Called for each argument in a call, performs required mappings'''
    if isinstance(for_param_or_type, SGType):
        the_type = for_param_or_type
    else:
        the_type = for_param_or_type.data_type
        
    if the_type.name in _data_switcher:
        #convert data using pattern from _data_switcher
        return _data_switcher[the_type.name] % arg_str
    else:
        return arg_str

def adapter_type_visitor(the_type):
    '''switch types for the python SwinGame adapter (links to DLL)'''
    name = None if the_type is None else the_type.name.lower()
    if name not in _adapter_type_switcher:
        logger.error('CREATE   : Error changing adapter type %s - %s', modifier, the_type)
    
    return _adapter_type_switcher[name]

def adapter_param_visitor(the_param, last):
    name = the_param.name.lower()
    if name not in _adapter_type_switcher:
        logger.error('CREATE   : Error visiting adapter parameter %s - %s', the_param.modifier, the_param.data_type.name)
        return 'XXX'
        #assert False
    
    return '%s%s' % (
        _adapter_type_switcher[name] % the_param.name,
        ', ' if not last else '')

def type_visitor(the_type, modifier = None):
    return "%s %%s" % ('void' if the_type is None else the_type.name)

def param_visitor(the_param, last):
    return '%s%s' % (
        type_visitor(the_param.data_type, the_param.modifier) % the_param.name,
        ', ' if not last else '')

# accumulates methods and prints them later
methods_visited = {} # calls.name -> [(method, name, details)]
IGNORE_METHODS = [
    'sg_Input_MouseWheelScroll',
    'sg_Geometry_VectorToString',
]

def method_visitor(the_method, other):
    details = the_method.to_keyed_dict(
        other['param visitor'], 
        other['type visitor'], 
        other['arg visitor'])
    if details['calls.name'] in IGNORE_METHODS:
        logging.warn('Skipping method %s', details['calls.name'])
        return other
    
    # check and cleanup doc strings ... % need to be %%, + line indent
    if '%' in details['doc']:
        details['doc'] = details['doc'].replace('%','%%')
    details['doc'] = '\n   '.join(line for line in details['doc'].splitlines())
    
    if (','.join(a.lstrip() for a in details['args'].split(',')) !=
            ','.join(a.lstrip() for a in details['calls.args'].split(','))):
        # it's an alias, which we need to wrap
        details['is_alias'] = True
    
    # parameter processing
    params = details['params'].split(', ')
    args = details['args'].split(',') # don't ask me why it's different
    if params[0]:
        # munge into Python-acceptable form
        shortparams = [p[:p.index(' ')] for p in params]
        # deal with result parameters added by post_parse_process
        lastp = params[-1]
        resultbufs = 1 if lastp[lastp.index(' ')+1:] == 'result' else 0
        if resultbufs:
            params = params[:-resultbufs]
            args = args[:-resultbufs]
            shortparams = shortparams[:-resultbufs]
        # fill in argument types for checking
        argtypes = [_adapter_type_switcher.get(p.lower(), p) for p in shortparams]
    else:
        shortparams = []
        argtypes = ''
        resultbufs = 0
    details['params'] = ', '.join(params)
    details['args'] = ', '.join(args).replace('bool(', '').replace(')', '')
    details['shortparams'] = ', '.join(shortparams)
    details['argtypes'] = ', '.join(argtypes)
    details['resultbufs'] = resultbufs
    details['pre_call'] = ''
    details['post_call'] = ''
    details['calls.args'] = details['calls.args'].replace('true', 'True').replace('false', 'False')
    
    # return type munging
    ret_type = details['return_type']
    ret_type = ret_type[:ret_type.index(' ')]
    ret_type = _adapter_type_switcher.get(ret_type.lower(), ret_type)
    details['return_type'] = ret_type
    
    methods_visited.setdefault(details['calls.name'], []).append(details)
    
    return other

def visited_methods_writer(details_list, writer):
    true_method_details = [d for d in details_list if not 'is_alias' in d]
    assert len(true_method_details) == 1
    true_method_details = true_method_details[0]
    
    def write_method(template, details):
        writer.write(template % details)
    
    true_method_uname = true_method_details['uname_lower']
    if true_method_uname in py_lib.special_cases:
        template = py_lib.special_cases[true_method_uname]
    elif true_method_details['return_type'] is None:
        #details['the_call'] = other['arg visitor']('%(calls.name)s(%(calls.args)s)' % details, None, the_method.return_type)
        template = py_lib.function
    else:
        template = py_lib.method
    write_method(template, true_method_details)
    
    for details in details_list:
        if details is true_method_details:
            continue
        details['is_alias'] = true_method_uname
        write_method(py_lib.alias, details)

def write_methods_for(member, other):
    '''Write out member methods'''
    global methods_visited
    methods_visited = {}
    member.visit_methods(method_visitor, other)
    if other['writer'] is not None:
        for k in sorted(methods_visited.keys()):
            details_list = methods_visited[k]
            visited_methods_writer(details_list, other['writer'])

def write_type_for(member, other):
    '''Write out a type (class, struct, enum, typedef)'''
    assert member.is_class or member.is_struct or member.is_enum or member.is_type
    writer = other['writer']
    # CLASS, TYPE, STRUCT(ARRAY)
    if member.is_class or member.is_type or (member.is_struct and member.wraps_array):
        #convert to resource pointer
        if member.is_pointer_wrapper:
            # assert len(member.fields) == 1
            the_type = member.data_type
        elif member.is_data_wrapper:
            assert len(member.fields) == 1
            the_type = member.fields['data'].data_type
        elif member.wraps_array:
            assert len(member.fields) == 1
            the_type = member.fields['data'].data_type
        elif member.data_type.is_procedure:
            assert member.data_type.method != None
            the_type = member.data_type
        else:
            logger.error('CREATE PYTHON  : Unknown class type for %s', member.uname)
            assert False
        writer.writeln('class %s(c_void_p): pass\n' % member.name)
    # PURE STRUCT
    elif member.is_struct:
        #class Point2D(Structure): # record/struct;
        #    _fields_ = [('x', c_float), (), ... ]
        writer.writeln('class %s(ByRefStructure):' % member.name)
        writer.writeln("    '''%s\n    '''" % '\n   '.join(member.doc.splitlines()))
        writer.writeln('    _fields_ = [')
        for field in member.field_list:
            writer.writeln('        (%r, %s),' % (field.name, adapter_type_visitor(field.data_type)))
        writer.writeln('    ]\n')
    # PURE ENUM
    elif member.is_enum:
        #enum id { list } 
        # basic -> (...) = map(c_int, range(length(...))
        # class object FontAlignment.Left etc
        #other['writer'].write(str(member) + str(dir(member)))
        writer.writeln('class %s(c_int_enum):' % member.name)
        writer.writeln("    '''%s\n    '''" % '\n   '.join(member.doc.splitlines()))
        for i, v in enumerate(member.values):
            v = v.replace('None', 'None_')
            if '=' in v:
                pass # nothing to do here; indices already provided
            else:
                v = v + ' = %d' % i # need to add indices
            writer.writeln('    %s' % v)
        writer.writeln('')
        

def write_py_module(the_file):
    '''Write the header and c file to wrap the attached files details'''
    with FileWriter(os.path.join(_out_path, the_file.name.lower() + '.py')) as mod:
        mod.writeln(py_lib.header % { 
            'name' : the_file.name,
            'pascal_name' : the_file.pascal_name,
        })
        
        for a_file in the_file.uses:
            if a_file.name != None:
                mod.writeln("from .%s import *\n" % a_file.name.lower())
        mod.writeln('')
        
        if the_file.name != 'SGSDK':
            mod.writeln(py_lib.header2)
        
        if the_file.name == 'Types':
            mod.writeln("from ._common import c_int_enum, ByRefStructure")
        
        #process all methods
        other = {
            'writer': mod,
            'type visitor': type_visitor,
            'param visitor': param_visitor,
            'arg visitor': arg_visitor
        }

        for m in the_file.members:
            if m.is_class or m.is_struct or m.is_enum or m.is_type:
                write_type_for(m, other)        
            elif m.is_module:
                write_methods_for(m, other)

def post_parse_process(the_file):
    ''' the c modules also wrap array return values and adds length parameters for arrays.'''
    logger.info('Post Processing %s for Python wrapper creation', the_file.name)
    
    for member in the_file.members:
        for key, method in member.methods.items():
            if method.method_called.was_function:
                #convert string return types
                result_param = SGParameter('result')
                result_param.data_type = method.return_type
                result_param.modifier = 'var'
                param_list = list(method.params)
                param_list.append(result_param)
                method.params = tuple(param_list)
                arg_list = list(method.args)
                arg_list.append(result_param)
                method.args = arg_list
                method.return_type = None
            if method.method_called.has_length_params:
                #add length parameters to this method
                for param in method.method_called.params:
                    if param.is_length_param:
                        raise RuntimeError("Uh oh! This case isn't properly developed yet")
                        param_list = list(method.params)
                        param_list.append(param)
                        method.params = tuple(param_list)
                        arg_list = list(method.args)
                        arg_list.append(param)
                        method.args = arg_list

def file_visitor(the_file, other):
    '''Called for each file read in by the parser'''
    # if the_file.name == 'SGSDK':
        # return
    post_parse_process(the_file)
    print(the_file.name)
    logger.info('Creating Python SwinGame Module %s', the_file.name)
    write_py_module(the_file)

def main():
    logging.basicConfig(level=logging.WARN,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        stream=sys.stderr)
    
    #load_data()
    parser_runner.run_for_all_units(file_visitor)

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass

    main()
