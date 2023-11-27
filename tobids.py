#!/usr/bin/env python3
# Dave Braun (2023)
import os
import sys
from glob import glob
from collections import OrderedDict
import json
from pathlib import Path
from mne_bids.path import BIDSPath
# Import custom modules
from helpers.validations import ValidateBasics, final_validation
from helpers.modality_agnostic import get_dataset_description
from helpers.modality_specific import (
        get_eeg_json, 
        get_channels_tsv,
        get_electrodes_tsv
)
from helpers.make_readme import initialize_readme, create_readme
from helpers.basic_parsing import (
        parse_command_line, 
        parse_subjects, 
        parse_data_type,
        make_skeleton
)
from helpers.eeg_tools import write_eeg
'''
delete if not needed
from helpers.create_eeg_dirs import (
        get_eeg_paths, 
        init_eeg_dir,
        load_raw_brainvision,
        make_bids_data,
        make_bids_filestem,
        write_file
)
'''
from helpers.mne_bids_mods import _write_dig_bids


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


if __name__ == '__main__':

    # Import dataset description
    dataset_description = get_dataset_description()
    
    # Parse user command line input
    origin_path, dest_path = parse_command_line(sys.argv[1:], dataset_description)

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

    # Determine whether there is eeg and / or fmri data
    eeg, fmri = parse_data_type(origin_path)

    # Set up basic directory structure
    make_skeleton(subjects, dest_path, eeg, fmri)

    # INITIALIZE TOP LEVEL FILES #
    # -- Compile dataset description
    with open(dest_path / Path('dataset_description.json'), 'w') as ff:
        json.dump(dataset_description, ff, sort_keys=False, indent=4)

    # -- Initialize a README
    create_readme(dest_path, dataset_description)

    # Iterate over subjects
    for subject in subjects:
        print('\nProcessing Subject {}'.format(subject['number']))

        # Handle sessions
        if subject['sessions']:
            sessions = list(subject['sessions'].keys())
        else:
            sessions = '-999'

        # Iterate over sessions
        for session in sessions:
            if sessions == '-999':
                session_path = Path('')
            else:
                session_path = subject['sessions'][session]

            seek_path = origin_path / subject['path'] / session_path
            # Build write path
            subject_arg = Path('sub-' + subject['number'])
            session_arg = Path('ses-' + session)
            write_path = dest_path / subject_arg / session_arg


            if eeg:
                # Get all *.eeg files for that subject/session
                eeg_files = glob(str(seek_path) + '/**/*.eeg', recursive=True)
                eeg_files = [Path(x) for x in eeg_files]

                write_eeg(eeg_files, write_path / Path('eeg'), make_edf)

            # dev
            fmri = False
            if fmri:
                # Get root fmri dir 
                # (the one with all the fmri dirs from the scan nested inside)
                fmri_root = glob(str(seek_path) + '/**/*.nii', recursive=True)
                fmri_root = Path(fmri_root[0]).parent.parent

                # This doesn't exist yet
                write_fmri(fmri_root, write_path)
    
    # Validate final directory
    final_validation(dest_path)
