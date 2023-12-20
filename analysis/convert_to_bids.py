#!/usr/bin/env python3

#SBATCH --time=00:05:00 # 5 for most subs, 10 for the rest
#SBATCH --partition=broadwl # broadwl for most subs, bigmem2 for rest
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=32G # 50 enough for most subs, 80 for rest
#SBATCH --mail-type=all
#SBATCH --mail-user=letitiayhho@uchicago.edu
#SBATCH --output=logs/convert-to-bids_%j.log

from mne_bids import BIDSPath, write_raw_bids, get_anonymization_daysback
import numpy as np
import itertools
import mne
import os
import sys

def main(fpath, sub) -> None:
    print(fpath, sub)

    task = 'expectationsABR'
    RAW_DIR = '../data/raw/'
    BIDS_DIR = '../data/bids/'

    # load data
    raw = mne.io.read_raw_brainvision(fpath)
    raw.load_data()

    # add line freq to info
    print("Add line_freq to raw.info")
    raw.info['line_freq'] = 60 # the power line frequency in the building we collected in
    
    # Set channel types
    raw.set_channel_types({'EP1': 'eeg', 'BIP1': 'stim'})

    # Extract events from raw file
    print("Set annotations")
    events, event_ids = mne.events_from_annotations(raw)

    # Drop meaningless event name
    events = np.array(events)
    events = events[events[:,2] != event_ids['New Segment/'], :]
    event_codes = events[:,2]
    
    # Rename events from random numbers to interpretable labels
    event_codes = events[:,2]
    event_names = {2: 'A-non-rand', 
                   3: 'F-non-rand',
                   4: 'G-non-rand',
                   5: 'A-inv-rand',
                   6: 'F-inv-rand',
                   7: 'G-inv-rand',
                   8: 'A-non-seq',
                   9: 'F-non-seq',
                   10: 'G-non-seq',
                   11: 'A-inv-seq',
                   12: 'F-inv-seq',
                   13: 'G-inv-seq',
                   14: 'noise', 
                   15: 'noise'}
    annot = mne.annotations_from_events(events, sfreq = raw.info['sfreq'], event_desc = event_names)
    raw = raw.set_annotations(annot)

    # Get range of dates the BIDS specification will accept
    daysback_min, daysback_max = get_anonymization_daysback(raw)

    # Write data into BIDS directory, while anonymizing
    print("Write data into BIDS directory")
    bids_path = BIDSPath(
            subject = sub,
            task = task,
            datatype = 'eeg',
            root = BIDS_DIR
    )

    write_raw_bids(
        raw,
        bids_path = bids_path,
        allow_preload = True, # whether to load full dataset into memory when copying
        format = 'BrainVision', # format to save to
        anonymize = dict(daysback = daysback_min), # shift dates by daysback
        overwrite = True,
    )

    # Check if conversion was successful and .vhdr file was written
    vhdr_path = str(bids_path)
    print(f".vhdr file written? {os.path.exists(vhdr_path)}")
    print("Done :-)")

__doc__ = "Usage: ./convert-to-bids.py <fpath> <sub> <task> <run> <bids_path>"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    fpath = sys.argv[1]
    sub = sys.argv[2]
    main(fpath, sub)
