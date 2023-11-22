#!/usr/bin/env python3
# Dave Braun (2023)
import os
import sys
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
        parse_data_type
)
from helpers.create_eeg_dirs import (
        get_base_filenames, 
        init_eeg_dir,
        load_raw_brainvision,
        make_bids_data,
        make_bids_filestem,
        write_file
)
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
    task_name = vb.confirm_task_name()


    # Create destination directory
    if not dest_path.exists():
        os.mkdir(dest_path)
    
    # Compile dataset description
    # ** Could expand this to a class to handle all Level 1 files
    with open(dest_path / Path('dataset_description.json'), 'w') as ff:
        json.dump(dataset_description, ff, sort_keys=False, indent=4)

    # Initialize a README
    create_readme(dest_path, dataset_description)

    # NEED TO ADD
    # participants.tsv, participants.json, task-TASKNAME_events.json

    # Load montage
    #montage = mne.channels.read_custom_montage(fname='./BC-MR3-32.bvef')

    # Get subject info
    # list of dict (each subject is element) with keys
        # number, path, sessions
        # sessions is a dict with key session number and value as path
    subjects = parse_subjects(origin_path)

    # Determine whether there is eeg and / or fmri data
    eeg, fmri = parse_data_type(origin_path)

    # Iterate over subjects
    for subject in subjects:
        print('\nProcessing Subject {}'.format(subject['number']))
        sys.exit(1)
        # Grab full file paths by run (without extensions))
        base_filenames = get_base_filenames(origin_dir, subject)
        # Make subject-specific BIDs files for each run
        for run, base_filename in enumerate(base_filenames):

            # Make bids filestem (ie, filename without suffix)
            bids_filestem = make_bids_filestem(subject,
                                               task_name,
                                               run)
            
            # Intervene around here to fork to eeg vs fmri

            # Make write directory string (no filename)
            write_dir = '/'.join([dest_dir, 
                                  'sub-{}'.format(subject),
                                  'eeg']) + '/'


            # Initialize EEG directory for a subject
            init_eeg_dir(subject, dest_dir)

            # Get raw data
            raw = load_raw_brainvision(base_filename)

            # Write / copy raw data to BIDs dir
            make_bids_data(dest_dir,
                           bids_filestem, 
                           raw, 
                           base_filename, 
                           subject,
                           make_edf=make_edf)

            # Compile and write *_eeg.json
            eeg_json = get_eeg_json(task_name, raw)
            write_file(eeg_json, write_dir, bids_filestem, 'eeg', '.json')

            # Unsure about *_events.tsv

            # Compile and write *_channels.tsv
            channels_tsv = get_channels_tsv(raw) 
            write_file(channels_tsv, 
                       write_dir, 
                       bids_filestem, 
                       'channels',
                       '.tsv')

            '''
            # Compile and write *_electrodes.tsv
            electrodes_tsv = get_electrodes_tsv(raw)
            write_file(electrodes_tsv,
                       write_dir,
                       bids_filestem,
                       'electrodes',
                       '.tsv')

            THE BELOW FUNCTION can't recover the coordinate system used
            it failed to be inferred from the montage
            it can be supplied to BIDSPath.space


            # Compile and write *_coordsystem.json
            bids_path = BIDSPath(subject=subject,
                                 task=task_name,
                                 run=run,
                                 suffix='coordsystem',
                                 extension='.json',
                                 datatype='eeg',
                                 root=dest_dir)

            _write_dig_bids(bids_path,
                            raw,
                            montage=montage,
                            overwrite=True)
            '''
    
    # Validate final directory
    final_validation(dest_dir)
