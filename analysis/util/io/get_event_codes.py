#!/usr/bin/env python3

#SBATCH --time=00:01:00
#SBATCH --partition=broadwl
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=16G
#SBATCH --mail-type=all
#SBATCH --mail-user=letitiayhho@uchicago.edu
#SBATCH --output=logs/get_event_codes_%j.log

import glob
import re
import sys
import mne
import numpy as np

def main(path):
    print(f"Reading {path}")
    epochs = mne.read_epochs(path)
    events = epochs.events[:,2]
    mapping = {10001: 100, 10002: 150, 10003: 200, 10004: 250, 10005: 50}
    events = np.vectorize(mapping.get)(events)

    sub = re.findall(r'sub-(\d{1,2})', path)[0]
    run = re.findall(r'run-(\d{1})', path)[0]
    save_path = f'../data/bids/derivatives/preprocessing/sub-{sub}/sub-{sub}_run-{run}_events.npy'
    print(f"Saving event tags to {save_path}")
    np.save(save_path, events)
    
if __name__ == "__main__":
    path = sys.argv[1]
    main(path)