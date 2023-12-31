#!/usr/bin/env python3

#SBATCH --time=02:00:00
#SBATCH --partition=bigmem2
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=128G
#SBATCH --mail-type=all
#SBATCH --mail-user=letitiayhho@uchicago.edu
#SBATCH --output=logs/preprocess_%j.log

import sys
import gc
import re
import mne
import numpy as np
from mne_bids import BIDSPath, read_raw_bids
from util.io.bids import DataSink

def main(sub) -> None:
    task = 'expectationsABR'

    # Constants
    BIDS_ROOT = '../data/bids'
    DERIV_ROOT = '../data/bids/derivatives'
    LOWPASS = 2000
    HIGHPASS = 100

    print("---------- Import data ----------")
    print(sub, task)
    bids_path = BIDSPath(root = BIDS_ROOT,
                        subject = sub,
                        task = task,
                        datatype = 'eeg',
                        )
    print(bids_path)
    raw = read_raw_bids(bids_path, verbose = False)
    raw.load_data()
    raw = raw.pick_types(eeg = True)
    events, event_ids = mne.events_from_annotations(raw)

    print("---------- Filtering ----------")
    raw = raw.filter(h_freq = LOWPASS, l_freq = HIGHPASS, picks = ['EP1'])
    line_freqs = np.arange(60, 181, 60)
    raw.notch_filter(line_freqs, picks = ['EP1'])

    print("---------- Epoch ----------")
    epochs = mne.Epochs(
        raw,
        events,
        tmin = -0.1,
        tmax = 0.1,
        baseline = None, # do NOT baseline correct the trials yet; we do that after ICA
        event_id = event_ids, # remember which epochs are associated with which condition
        preload = True # keep data in memory
    )
    
    print("---------- Trial rejection ----------")
    epochs.drop_bad(reject = dict(eeg = 35e-6))

    print("---------- Save results and generate report ----------")
    sink = DataSink(DERIV_ROOT, 'preprocess')

    # save cleaned data
    fpath = sink.get_path(
                    subject = sub,
                    task = task,
                    desc = 'clean',
                    suffix = 'epo', # this suffix is following MNE, not BIDS, naming conventions
                    extension = 'fif.gz',
                    )
    epochs.save(fpath, overwrite = True)

__doc__ = "Usage: ./preprocess.py <sub>"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    sub = sys.argv[1]
    main(sub)
