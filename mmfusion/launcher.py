import argparse
import os
import sys

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-V', '--version', default=9)
    args, unknown = parser.parse_known_args()

    if sys.platform == 'darwin':
        exec_path = '/Applications/Blackmagic Fusion {}/Fusion.app/Contents/MacOS/Fusion'.format(args.version)
    else:
        exec_path = '/opt/BlackmagicDesign/Fusion{}/Fusion'.format(args.version)

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
    os.execve(exec_args[0], exec_args, env)
