#!/usr/bin/env python

from __future__ import print_function

import os
import os.path as path
import shutil
import argparse
import subprocess
from sys import argv, exit
from distutils.dir_util import copy_tree
from glob import glob

if 'raw_input' in globals():
    input = raw_input

def safe_makedirs(dir):
    try:
        os.makedirs(dir)
    except OSError:
        pass

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

    icon = u'SwinGame'
    if osname == osnames[u'mac']:
        icon += u'.icns'

    full_app_path, app_path, game_main = app_path, u'.', u''

    out_dir, tmp_dir, src_dir, lib_dir, log_file = [path.join(app_path, p) for p in [u'bin', u'tmp', u'src', u'lib', u'out.log']]
    full_out_dir = path.join(full_app_path, u'bin')

    arg_parser = argparse.ArgumentParser(description=u'Compiles your game into an executable application. Output is located in %s.' % out_dir)
    arg_parser.add_argument('name',
                            nargs='?', default=game_name,
                            help=u'name of game (default: name of containing folder: %(default)s)')
    arg_parser.add_argument('-c', '--clean',
                            action='store_true',
                            help=u'perform a clean rather than a build')
    # arg_parser.add_argument('-i', '--icon',
                            # default=icon,
                            # help=u'change the icon file (default: %(default)s)')
    arg_parser.add_argument('-r', '--release',
                            action='store_true',
                            help=u'create a release version that does not include debug information')
    # arg_parser.add_argument('--windows64', '--win64', '--w64',
                            # action='store_true',
                            # help=u'when compiling on Windows, target 64-bit (default: 32-bit)')
    args = arg_parser.parse_args()
    
    # override game name?
    game_name = args.name
    
    # locate main file
    candidates = tuple(f for f in os.listdir(src_dir) if f.endswith(u'.py'))
    if len(candidates) == 1:
        game_main = candidates[0]
    else:
        print(u'Select the code file to compile for your game')
        for i, f in enumerate(candidates):
            print(u' ', i, u':', f)
        game_main = candidates[int(input(u'File number: '))]
    game_main = path.join(src_dir, game_main)
    # sanity check
    if not path.isfile(game_main):
        print(u'Cannot find file to compile: was looking for', game_main)
        exit(-1)
    
    # select out_dir subdir
    out_dir = path.join(out_dir, u'Release' if args.release else u'Debug')
    
    safe_makedirs(out_dir)
    safe_makedirs(tmp_dir)
    
    # actually compile
    if args.clean:
        shutil.rmtree(tmp_dir)
        os.mkdir(tmp_dir)
        shutil.rmtree(out_dir)
        os.mkdir(out_dir)
        print(u'... Cleaned')
    else:
        print(u'''\
--------------------------------------------------
          Creating %s
          for %s
--------------------------------------------------
  Running script from %s
  Saving output to %s
--------------------------------------------------
''' % (game_name, osname, full_app_path, out_dir))
        os.chdir(full_app_path)
        if osname == osnames[u'mac']:
            pass # TODO Mac-specific stuff
        # TODO presently a bit minimal
        try:
            copy_tree(src_dir, tmp_dir)
            copy_tree(lib_dir, tmp_dir)
            shutil.copy2(game_main, path.join(tmp_dir, u'__main__.py'))
            archive_name = shutil.make_archive(game_name, u'zip', root_dir=tmp_dir)
            shutil.move(archive_name, path.join(out_dir, game_name + u'.pyz'))
            for dll in glob(path.join(lib_dir, 'swingame', '*.dll')):
                shutil.copy2(dll, path.join(out_dir, path.basename(dll)))
        except Exception:
            print(u'Something went wrong while compiling! Details follow\n')
            raise
    
    #os.remove(log_file) # never created
    print(u'  Finished\n--------------------------------------------------')
