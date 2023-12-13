#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
from util.io.preprocessing import get_save_path
from util.io.iter_BIDSPaths import *

def main(subs, skips) -> None:
    BIDS_ROOT = '../data/bids'
    DERIV_ROOT = '../data/bids/derivatives'
    layout = BIDSLayout(BIDS_ROOT, derivatives = False)
    subs = layout.get_subjects()
    
    for sub in subs:
        print("subprocess.check_call(\"sbatch ./preprocess.py {sub}\" % (sub), shell=True)")
        subprocess.check_call("sbatch ./preprocess.py %s" % (sub), shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run preprocess.py over given subjects')
    parser.add_argument('--subs', 
                        type = str, 
                        nargs = '*', 
                        help = 'subjects to preprocess (e.g. 3 14 8), provide no argument to run over all subjects', 
                        default = [])
    parser.add_argument('--skips', 
                        type = str, 
                        nargs = '*', 
                        help = 'subjects NOT to preprocess (e.g. 1 9)', 
                        default = [])
    args = parser.parse_args()
    subs = args.subs
    skips = args.skips
    print(f"subs: {subs}, skips : {skips}")
    if bool(subs) & bool(skips):
        raise ValueError('Cannot specify both subs and skips')
    main(subs, skips)
