from __future__ import print_function

import atexit
import argparse
import os
import random
import subprocess
import sys
import time


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-V', '--version', default=9)
    parser.add_argument('--render', '-render', action='store_true')
    parser.add_argument('--license-retries', type=int, default=0, metavar='NUM',
        help="Skip default behaviour of retrying command on license failures.")
    parser.add_argument('--assert-mm', action='store_true', help=argparse.SUPPRESS) # For the render script.
    args, unknown = parser.parse_known_args()


    env_diff = {}

    if sys.platform == 'darwin':
        if args.render:
            print("[mmfusion] -render not implemented on macOS", file=sys.stderr)
            exit(1)
        exec_path = '/Applications/Blackmagic Fusion {}/Fusion.app/Contents/MacOS/Fusion'.format(args.version)
        exec_args = [exec_path]

    else:
        exec_path = '/opt/BlackmagicDesign/Fusion{mode}{version}/Fusion{mode}'.format(
            mode='RenderNode' if args.render else '',
            version=args.version,
        )
        if args.render:

            # We need to get a display with Xvfb. We were having trouble with
            # xvfb-run (it was colliding with itself using display 99, the
            # auto-display function didn't seem to work), so we implemented it
            # ourselves here. Hilariously, our licensing problems seem to have
            # gone away at the same time.
            xvfb = subprocess.Popen(['Xvfb',
                '-nolisten', 'tcp',
                '-displayfd', '1', # It will write the display number to stdout.
                '-screen', '0', '640x480x24',
            ], stdout=subprocess.PIPE)
            atexit.register(xvfb.kill)
            display = int(xvfb.stdout.readline())

            print("[mmfusion] Xvfb serving display :{} in process {}.".format(display, xvfb.pid), file=sys.stderr)

            env_diff['DISPLAY'] = ':{}'.format(display)
            exec_args=[exec_path, '-render']

        else:
            exec_args = [exec_path]

    exec_args.extend(unknown)

    here = os.path.abspath(os.path.join(__file__, '..'))

    
    # Hook the preferences.
    env_diff['FUSION{}_MasterPrefs'.format(args.version)] = os.path.join(here, 'MasterPrefs.prefs')

    # Give our preferences a path to work with.
    env_diff['MMFUSION'] = here

    env = os.environ.copy()
    env.update(env_diff)

    retries = args.license_retries
    while True:

        completed_successfully = False
        missing_license_server = False

        proc = subprocess.Popen(exec_args, env=env, stdout=subprocess.PIPE, bufsize=1)

        while True:
            
            # The `for line in proc.stdout` will not yield lines until the
            # command has finished, so we need to implement it ourselves.
            line = proc.stdout.readline()
            if not line:
                break

            if line.startswith('Render completed successfully'):
                completed_successfully = True
            elif line.startswith('Cannot locate license server'):
                missing_license_server = True

            sys.stdout.write(line)
            sys.stdout.flush()

        code = proc.returncode

        # We only care if there was an error AND we were missing the license server.
        if not code or not missing_license_server:
            exit(code)

        if completed_successfully:
            print("[mmfusion]: Ignoring exit code {} due to reported success.".format(code), file=sys.stderr)
            exit(0)

        if not retries:
            print("[mmfusion] No more retries.", file=sys.stderr)
            exit(code)

        delay = 5 * random.random()
        print("[mmfusion] Failed with code {} due to license failure. Retrying in {:.1f}s. {} retries left.".format(
            code, delay, retries), file=sys.stderr)
        retries -= 1
        time.sleep(delay)


if __name__ == '__main__':
    main()
