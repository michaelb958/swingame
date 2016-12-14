#!/usr/bin/env python2

from __future__ import print_function

import os
import os.path as path
import shutil
import argparse
from sys import argv, exit

if __name__ == '__main__':
    app_path = path.dirname(argv[0])
    if not app_path:
        exit(-1)
    os.chdir(app_path)
    app_path = os.getcwd()

    game_name = path.basename(app_path)
    
    arg_parser = argparse.ArgumentParser(description=u'Cleans internal build directories, allowing you to compile your game from a fresh state.')
    args = arg_parser.parse_args()

    print(u'''\
    --------------------------------------------------
              Cleaning Up %s
    --------------------------------------------------''' % game_name)

    def clean_folder(name):
        shutil.rmtree(path.join(app_path, name), ignore_errors=True)
        os.mkdir(path.join(app_path, name))
        print u' * Cleaned', name, u'folder'
    clean_folder(u'tmp')
    clean_folder(u'bin')

    try:
        from subprocess import call
        call(path.join(app_path, u'lib', u'cleanlib.sh'))
    except:
        pass

    print(u'--------------------------------------------------')
