# Dave Braun (2023)

from pathlib import Path
import json
import shutil
import pandas as pd
from glob import glob
import mne
import os
# see here for example: https://github.com/holgern/pyedflib
from pyedflib import highlevel

'''
Need to comment throughout
I need to determine if base_filename has a trailing /
'''


def get_eeg_paths(origin_path, subject):
    '''
    This function takes as input:
        The origin directory
        A subject id (eg, 006)
    Returns list of Path objects to each *.eeg file for a subject

    Assumes files are labeled in order of run number
    '''
    # Grab raw file names
    base_filenames = glob(str(origin_path / Path(subject['path'])) + '/**/*.eeg', recursive=True)
    # Sort in order of run number
    base_filenames= sorted(base_filenames)
    # Keep only unique
    base_filenames = list(set(base_filenames))

    return [Path(x) for x in base_filenames]

def init_eeg_dir(subject, dest_dir):
    '''
    Take as input a subject and destination directory
    Initialize the eeg directory for that subject
    '''
    to_make = '/'.join([dest_dir, 'sub-{}'.format(subject), 'eeg'])
    
    if not os.path.exists(to_make):
        os.makedirs(to_make)



def make_bids_data(dest_dir, bids_filestem, raw, base_filename, subject, make_edf):
    '''
    Writes BIDs compatible data in the destination directory

    PARAMETERS
    ----------
    dest_dir: Destination directory
    bids_filestem: A BIDs compatible filestem 
                    (eg, sub-006_task-MWEEG_run-00)
    raw: mne.io.Raw
    base_filename: A path to one subject's one run with the filename
                    without an extension.
    make_edf: boolean
              whether or not to write an edf file or move the brainvision
              triplet
    '''

    # Make a full write path (without extension)
    write_path = dest_dir + '/' + 'sub-{}/'.format(subject) + 'eeg/' +\
                    bids_filestem + '_eeg'
    if make_edf:
        # Get channel names
        channel_names = raw.info['ch_names']
        sf = raw.info['sfreq']
        signal_headers = highlevel.make_signal_headers(channel_names, 
                                                       sample_frequency=sf)
        highlevel.write_edf(write_path + '.edf', 
                            raw.get_data(), 
                            signal_headers)
        print('\nSaved: {}'.format(bids_filestem + '_eeg.edf'))

    else:
        extensions = ['.eeg', '.vhdr', '.vmrk']
        filestem = _get_filestem(base_filename)

        for extension in extensions:
            source_file = base_filename + extension
            shutil.copy(source_file, write_path + extension)
            

def make_bids_filestem(subject, task_name, run):
    '''
    Produces a bids compatible filestem 
    (eg, sub-<label>_task-<TASKNAME>_run-<RUN>)

    PARAMETERS
    ----------
    subject: (string) subject number
    task_name: (string) task name
    run: (string) run number
    '''
    # Format run with three digits
    run = str(run).zfill(3)

    return '_'.join(['sub-{}'.format(subject),
                     'task-{}'.format(task_name),
                     'run-{}'.format(run)])

def write_file(data, write_path, suffix, extension):
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
    
    write_str = str(write_path) + '_' + suffix + extension
    
    if extension == '.tsv':
        data.to_csv(write_str, sep='\t', index=False)

    elif extension == '.json':
        with open(write_str, 'w') as file:
            json.dump(data, file)

    else:
        raise ValueError('Extension must be .tsv or .json')




# --- INTERNAL UTILITY FUNCTIONS ---
def _get_directory_path(path):
    '''
    Takes as input either a full path or base filename
    Returns just the directory path (no filename)
    Directory path has a trailing /
    '''
    path = path.split('/')[:-1]
    return '/'.join(path) + '/'
    
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







