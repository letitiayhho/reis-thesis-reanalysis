#!/usr/bin/env python3

import argparse
import subprocess
import glob
import re

def main(subs, skips) -> None:

    for fpath in glob.glob('../data/raw/Subj*.vhdr'):
        # Get subject number
        regex = re.compile(r'\d+')
        sub = regex.findall(fpath)[0]

        # Run script on file
        #subprocess.check_call("sbatch ./convert_to_bids.py %s %s" % (fpath, sub), shell=True)
#         print(fpath, sub)
        subprocess.check_call("./convert_to_bids.py %s %s" % (fpath, sub), shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run convert-to-bids.py over given subjects')
    parser.add_argument('--subs',
                        type = str,
                        nargs = '*',
                        help = 'subjects to convert (e.g. 3 14 8), provide no argument to run over all subjects',
                        default = [])
    parser.add_argument('--skips',
                        type = str,
                        nargs = '*',
                        help = 'subjects NOT to convert (e.g. 1 9)',
                        default = [])
    args = parser.parse_args()
    subs = args.subs
    skips = args.skips
    print(f"subs: {subs}, skips : {skips}")
    if bool(subs) & bool(skips):
        raise ValueError('Cannot specify both subs and skips')
    main(subs, skips)
