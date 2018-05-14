from __future__ import print_function

import argparse
import os
import sys

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-V', '--version', default=9)
    parser.add_argument('--render', '-render', action='store_true')
    parser.add_argument('--assert-mm', action='store_true', help=argparse.SUPPRESS) # For the render script.
    args, unknown = parser.parse_known_args()

    if sys.platform == 'darwin':
        if args.render:
            print("--render not implemented on macOS")
            exit(1)
        exec_path = '/Applications/Blackmagic Fusion {}/Fusion.app/Contents/MacOS/Fusion'.format(args.version)
        exec_args = [exec_path]

    else:
        exec_path = '/opt/BlackmagicDesign/Fusion{mode}{version}/Fusion{mode}'.format(
            mode='RenderNode' if args.render else '',
            version=args.version,
        )
        if args.render:
            exec_args=['xvfb-run', '-s', '-screen 0 640x480x24', exec_path, '-render']
        else:
            exec_args = [exec_path]

    exec_args.extend(unknown)

    here = os.path.abspath(os.path.join(__file__, '..'))

    env_diff = {}
    
    # Hook the preferences.
    env_diff['FUSION{}_MasterPrefs'.format(args.version)] = os.path.join(here, 'MasterPrefs.prefs')

    # Give our preferences a path to work with.
    env_diff['MMFUSION'] = here

    env = os.environ.copy()
    env.update(env_diff)
    os.execvpe(exec_args[0], exec_args, env)
