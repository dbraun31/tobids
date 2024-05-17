#!/usr/bin/env python
# Dave Braun (2023)
import os
import sys
from tqdm import tqdm
from glob import glob
from collections import OrderedDict
import json
from pathlib import Path
from mne_bids.path import BIDSPath
# Import custom modules
from helpers.validations import ValidateBasics, final_validation
from helpers.validations import validate_task_names
from helpers.modality_specific import (
        get_eeg_json, 
        get_channels_tsv,
        get_electrodes_tsv
)
from helpers.basic_parsing import (
        parse_command_line, 
        parse_subjects, 
        parse_data_type,
        make_skeleton,
        configure_progress_bar,
        get_overwrite
)
from helpers.eeg_tools import write_eeg
from helpers.mne_bids_mods import _write_dig_bids
from helpers.fmri_tools import (write_fmri, get_fmri_root)
from helpers.metadata import make_metadata


'''
This script should be executed from the command line with Python.
It has one required command line argument, which is the directory of the raw data to
be converted. 
A destination directory can optionally be provided 
Otherwise, destination directory will be the dataset name (set in the
dataset_description.json) with suffix _BIDS


'''

# Decide whether to write raw data to .edf or just copy it as is
make_edf = False
# Rely on mne_bids for writing eeg data and meta data?
use_mne_bids = True

if __name__ == '__main__':

    # Parse user command line input
    origin_path, dest_path = parse_command_line(sys.argv[1:])

    # Put everthing inside 'rawdata'
    dest_path = dest_path / Path('rawdata')

    # Whether to overwrite existing data
    overwrite = get_overwrite()

    # Initialize and run basic validation
    # see helpers/validation.py
    vb = ValidateBasics(origin_path)
    vb.confirm_subject_count()
    vb.confirm_subject_data()

    # Get subject info
    # list of dict (each subject is element) with keys
        # number, path, sessions
        # sessions is a dict with key session number and value as path
    subjects = parse_subjects(origin_path)

    # Check with user
    validate_task_names(subjects, origin_path)
    
    # Init progress bar
    progress_bar = configure_progress_bar(origin_path)

    # Iterate over subjects
    for subject in subjects:
        print('\nProcessing Subject {}'.format(subject['number']))

        # Handle sessions
        if subject['sessions']:
            sessions = list(subject['sessions'].keys())
        else:
            sessions = ['-999']

        # Iterate over sessions
        for session in sessions:
            if sessions[0] == '-999':
                session_path = Path('')
                session_arg = Path('')
            else:
                session_path = subject['sessions'][session]
                session_arg = Path('ses-' + session)

            seek_path = origin_path / subject['path'] / session_path
            # Build write path
            subject_arg = Path('sub-' + subject['number'])

            write_path = dest_path / subject_arg / session_arg

            # Determine whether there is eeg and / or fmri data
            eeg, fmri = parse_data_type(seek_path)

            if eeg:
                print('Writing EEG data')
                # Get all *.eeg files for that subject/session
                eeg_files = glob(str(seek_path) + '/**/*.eeg', recursive=True)
                eeg_files = [Path(x) for x in eeg_files]
                write_eeg(eeg_files, 
                          write_path / Path('eeg'), 
                          make_edf,
                          overwrite,
                          use_mne_bids,
                          progress_bar)

            if fmri:
                print('Writing fMRI data')
                # Get root fmri dir 
                # (the one with all the fmri dirs from the scan nested inside)
                fmri_root = get_fmri_root(seek_path)
                meta_info = {'subject': str(subject_arg), 'session': str(session_arg)}
                write_fmri(fmri_root, write_path, meta_info, overwrite, progress_bar)
    

    # Stick behavioral data processing around here

    # Make metadata if it doesn't exist
    make_metadata(dest_path)

    # Validate final directory
    final_validation(dest_path)


