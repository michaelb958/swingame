#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

Created by Andrew Cain on 2011-01-19.
Copyright (c) 2011 Swinburne University. All rights reserved.
"""

import sys
import os

_type_switcher = {
    'int64':    'int64',
    'single': 'Single',
    'longint': 'Longint',
    'word': 'Word',

    'string': 'PChar',
    'color': 'LongWord',
    'timer': 'Timer',
    'byte': 'Byte',
    'resourcekind': 'ResourceKind',
    'longword': 'Longword',
    'bitmap': 'Bitmap',
    'matrix2d': 'Matrix2D',
    'triangle': 'Triangle',
    'linesegment': 'LineSegment',
    'point2d': 'Point2D',
    'vector': 'Vector',
    'rectangle': 'Rectangle',
    'quad': 'Quad',
    'sprite': 'Sprite',

    'font': 'Font',
    'fontalignment': 'FontAlignment',
    'fontstyle': 'FontStyle',
    'mousebutton': 'MouseButton',
    'boolean': 'Boolean',
    'longbool': 'LongBool',
    'keycode': 'KeyCode',

    'linesarray':               'LineSegmentPtr',
    'resolutionarray':          'ResolutionPtr',
    'fingerarray':              'FingerPtr',
    'longintarray':             'LongintPtr',
    'bitmaparray':              'BitmapPtr',
    'point2darray':             'Point2DPtr',
    'trianglearray':            'TrianglePtr',
    'spriteeventhandlerarray':  'SpriteEventHandlerPtr',
    'stringarray':              'StringPtr',

    'spriteendingaction':       'SpriteEndingAction',
    'circle': 'Circle',
    'map': 'Map',
    'maptag': 'MapTag',
    'spritekind': 'SpriteKind',

    # Function Pointers
    'freenotifier':             'FreeNotifier',
    'spriteeventhandler':       'SpriteEventHandler',
    'spritefunction':           'SpriteFunction',
    'spritesinglefunction':     'SpriteSingleFunction',


    #...
    'shapeprototype': 'ShapePrototype',
    'shape': 'Shape',

    'shapekind':            'ShapeKind',
    'animation':            'Animation',
    'animationscript':      'AnimationScript',
    'collisiontestkind':    'CollisionTestKind',

    'bitmapcell':           'BitmapCell',
    'finger':               'Finger',
    'resolution':           'Resolution',

    'soundeffect':          'SoundEffect',
    'music':                'Music',

    'window':               'Window',

    'panel':                'Panel',
    'region':               'Region',
    'eventkind':            'EventKind',
    'filedialogselecttype': 'FileDialogSelectType',
    'guieventcallback':     'GUIEventCallback',

    'connection'        :   'Connection',
    'serversocket'        :   'ServerSocket',
    'arduinodevice'     :   'ArduinoDevice',

    'httpheader' : 'HttpHeader',
    'httpresponse' : 'HttpResponse',
    'httprequest' : 'HttpRequest',
    'httpmethod': 'HttpMethod',
    'connectiontype': 'ConnectionType',

    'drawingoptions': 'DrawingOptions',
    'message' : 'Message',
    'serversocket': 'ServerSocket',

    'guielementkind': 'GUIElementKind',

}


def main():
    '''Load all of the files in this directory into attributes of this module.'''
    (path, script_file) = os.path.split(sys.modules[__name__].__file__)
    dirList=os.listdir(path)

    for f in dirList:
        if '.py' in f or f[0] == '.' : continue

        (dirName, fileName) = os.path.split(f)
        key = fileName.replace('.', '_')
        #print key

        fin = open(path + '/' + f)
        data = fin.read()
        fin.close()

        setattr(sys.modules[__name__], key, data)



main()
