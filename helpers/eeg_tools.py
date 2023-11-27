import sys
import os
import json
import shutil
from pathlib import Path
from pyedflib import highlevel
from helpers.modality_specific import (
    get_eeg_json,
    get_channels_tsv
)
import mne

## still need all the imports =(


def write_eeg(eeg_files, write_path, make_edf):
    '''
    Takes as input list of *.eeg files for one subject / session
    And the start of the write path (dest/sub-<>/ses-<>/eeg)
    '''

    # Get list of task names
    tasks = list(set([x.parent.name for x in eeg_files]))
    
    for task_name in tasks:
        # Keep only relevant files
        task_files = [x for x in eeg_files if task_name in str(x)]
        # Sort them by run
        if len(task_files) > 1:
            task_files = sorted(task_files, key=_sort_task_files)

        for run, read_path in enumerate(task_files, start=1):
            # Build write file name
            subject = write_path.parent.parent.name
            session = write_path.parent.name
            task = 'task-{}'.format(task_name)
            run = 'run-{}'.format(str(run).zfill(3))
            write_filename = '_'.join([subject, session, task, run])
            write_stem = write_path / Path(write_filename)

            # Start writing files
            raw = _load_raw_brainvision(read_path)
            _make_bids_data(read_path, write_stem, raw, make_edf)
            # Compile and write eeg metadata
            eeg_json = get_eeg_json(task_name, raw)
            _write_file(eeg_json, write_stem, 'eeg', '.json')
            channels_tsv = get_channels_tsv(raw) 
            _write_file(channels_tsv, write_stem, 'channels', '.tsv')



## INTERNAL UTILITIES ##

def _sort_task_files(task_file):
    '''
    Input one .eeg file
    Returns the last digits in the string
    (used as a key for sorting)
    does a smart sort (ie, handles one and two digits appropriately)
    '''
    s = task_file.stem.rsplit('_', -1)[::-1]
    for e in s:
        try:
            return int(e)
        except ValueError:
            pass

    raise ValueError('EEG files need a run number somewhere in the file name')


def _load_raw_brainvision(read_path):
    '''
    Takes in full read path as Path object
    Returns the raw data as mne object
    '''

    read_stem = read_path.parent / read_path.stem
    with open(str(read_stem) + '.vhdr', 'r') as old_file:
        with open(str(read_path.parent) + '/temp.vhdr', 'w') as new_file:
            for line in old_file:
                if 'DataFile' in line:
                    line = 'DataFile={}'.format(str(read_path.stem) + '.eeg\n')
                if 'MarkerFile' in line:
                    line = 'MarkerFile={}'.format(str(read_path.stem) + '.vmrk\n')
                new_file.write(line)
    new_file.close()

    # Load data
    raw = mne.io.read_raw_brainvision(str(read_path.parent) + '/temp.vhdr', 
                                      preload=False,
                                      verbose='error')
    # Remove temporary vhdr
    os.remove(str(read_path.parent) + '/temp.vhdr')
    return raw

def _make_bids_data(read_path, write_stem, raw, make_edf):
    '''
    Writes BIDs compatible data in the destination directory

    PARAMETERS
    ----------
    read_path: the full path to an .eeg file (with extension)
    write_path: the full path and beginning of file name (without suffix or
                extension)
    raw: mne.io.Raw
    base_filename: A path to one subject's one run with the filename
                    without an extension.
    make_edf: boolean
              whether or not to write an edf file or move the brainvision
              triplet
    '''

    if make_edf:
        # Get channel names
        channel_names = raw.info['ch_names']
        sf = raw.info['sfreq']
        signal_headers = highlevel.make_signal_headers(channel_names, 
                                                       sample_frequency=sf)
        highlevel.write_edf(str(write_stem) + '_eeg.edf', 
                            raw.get_data(), 
                            signal_headers)
        print('\nSaved: {}'.format(str(write_stem) + '_eeg.edf'))

    else:
        extensions = ['.eeg', '.vhdr', '.vmrk']
        #filestem = _get_filestem(base_filename)

        for extension in extensions:
            source_file = str(read_path.parent / read_path.stem) + extension
            shutil.copy(source_file, str(write_stem) + '_eeg' + extension)

def _write_file(data, write_stem, suffix, extension):
    '''
    Writes out a BIDS compatible metadata (.tsv, .json) file

    PARAMETERS
    ----------
    data: OrederedDict or pd.Dataframe
            data to be written 
    write_dir: str; BIDs directory to write to (with trailing /)
    bids_filename: str; BIDs compatible filename (no extension; no suffix)
    suffix: str; last part of the BIDs file name (eg, _channels)
    extension: str; extension of file to write (eg, .tsv)
    '''
    
    write_str = str(write_stem) + '_' + suffix + extension
    
    if extension == '.tsv':
        data.to_csv(write_str, sep='\t', index=False)

    elif extension == '.json':
        with open(write_str, 'w') as file:
            json.dump(data, file)

    else:
        raise ValueError('Extension must be .tsv or .json')


def _get_filestem(path):
    '''
    Takes in a path containing file name either with or without an
    extension
    Returns just the filename without extension
    '''
    filename = path.split('/')[-1]
    if '.' in filename:
        filename = filename.split('.')[0]
    return filename


