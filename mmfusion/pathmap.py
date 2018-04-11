from __future__ import print_function

import argparse
import os
import re
import shutil


def fix_main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--backup', default='.pre-fix-pathmap')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('script')
    args = parser.parse_args()


    def sub(m):
        path = m.group(1)
        if path.startswith('K:'):
            if args.verbose:
                print(path)
            path = '/Volumes/CGroot' + path[2:]
        return '"{}"'.format(path)

    old_source = open(args.script).read()
    new_source = re.sub(r'"([^"]*)"', sub, old_source)

    if old_source == new_source:
        print 'No changes.'
        return

    if args.backup:
        backup = args.script + args.backup
        shutil.copy(args.script, backup)

    with open(args.script, 'w') as fh:
        fh.write(new_source)


