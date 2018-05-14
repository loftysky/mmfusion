from __future__ import print_function

import argparse
import os
import re
import sys


def submit_main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name')
    parser.add_argument('-s', '--start', type=int)
    parser.add_argument('-e', '--end', type=int)
    parser.add_argument('-c', '--chunk', type=int, default=5)
    parser.add_argument('script')
    args = parser.parse_args()

    if args.start is None and args.end is None:
        comp = open(args.script).read()
        m = re.search(r'''
            RenderRange\s*=\s*
            \{\s*
                (\d+)\s*,\s*
                (\d+)\s*
            \}''', comp, flags=re.VERBOSE)
        if not m:
            print("Could not parse RenderRange from {}.".format(args.script), file=sys.stderr)
            exit(1)
        args.start = int(m.group(1))
        args.end = int(m.group(2))

    elif args.start is None or args.end is None:
        print("Cannot provide only one of --start or --end.", file=sys.stderr)
        exit(2)

    args.name = args.name or 'Fusion :: {}'.format(os.path.splitext(os.path.basename(args.script))[0])


    from farmsoup.client import Client

    client = Client()
    job = client.job(
        name=args.name,
        reservations={'fusion': 1},
    ).setup_as_subprocess([
        'mmfusion', '--assert-mm',
        args.script,
        '-render',
        '-start', '@F',
        '-end', '@F_end',
    ])
    job.expand_via_range('F={}-{}/{}'.format(args.start, args.end, args.chunk))

    group = client.submit(
        name=args.name,
        jobs=[job],
    )

    print(group.id)
