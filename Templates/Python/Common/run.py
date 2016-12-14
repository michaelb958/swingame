#!/usr/bin/env python2

from __future__ import print_function

import os
import os.path as path
import argparse
import subprocess
import runpy
from sys import argv, stderr

if __name__ == '__main__':
    osnames = {
        u'mac': u'Mac OS X',
        u'win': u'Windows',
        u'lin': u'Linux',
    }

    osname = subprocess.check_output([u'uname']).decode(u'utf8')
    if osname == u'Darwin':
        osname = osnames[u'mac']
    elif osname == u'Linux':
        osname = osnames[u'lin']
    else:
        osname = osnames[u'win']

    app_path = path.dirname(argv[0])
    if not app_path:
        exit(-1)
    os.chdir(app_path)
    app_path = os.getcwd()

    game_name = path.basename(app_path)
    
    # override game name?
    arg_parser = argparse.ArgumentParser(description=u'Runs your game, compiled with build.py.')
    arg_parser.add_argument('name',
                            nargs='?', default=game_name,
                            help=u'name of game (default: name of containing folder: %(default)s)')
    args = arg_parser.parse_args()
    game_name = args.name

    def get_version_path(v):
        pathlist = ['.', u'bin', v, game_name]
        if osname == osnames['mac']:
            pathlist[-1] += u'.app'
            pathlist += [u'Contents', u'MacOS', game_name]
        pathlist[-1] += u'.pyz'
        return path.join(*pathlist)

    exe_path, version = None, None
    for v in [u'Debug', u'Release']:
        exe_path = get_version_path(v)
        if path.isfile(exe_path):
            version = v
            break
    else:
        stderr.write(u'Please build the game using %s\n' % path.join('.', 'build.py'))
        exit(-1)

    print(u'Running', version, u'version from', path.dirname(exe_path))

    if osname == osnames['mac']:
        applescript = path.join(app_path, u'lib', u'bring_fg.scpt')
        if not path.isfile(applescript):
            with open(applescript, 'w') as f:
                f.write(u'''\
on run argv
    try
        Delay(0.5)
        set proc to "" & item 1 of argv & ""
        tell application "System Events"
            tell process proc
                set frontmost to true
            end tell
        end tell
    on error
    end try
    return
end run''')
        subprocess.Popen([applescript, game_name])
    runpy.run_path(exe_path, run_name='__main__')
