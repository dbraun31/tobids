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
import mne_bids
from helpers.metadata import make_write_log



def write_eeg(eeg_files, write_path, make_edf, overwrite, use_mne_bids, progress_bar):
    '''
    Takes as input list of *.eeg files for one subject / session
    And the start of the write path (dest/sub-<>/ses-<>/eeg)
    '''

    write_path = write_path / Path('eeg')

    # Logging
    ins = []
    outs = []

    # Get list of task names
    tasks = list(set([x.parent.name for x in eeg_files]))

    for task_name in tasks:
        # Keep only relevant files
        task_files = [x for x in eeg_files if str(x.parent.name).lower() == task_name.lower()]

        # Sort them by run
        if len(task_files) > 1:
            task_files = sorted(task_files, key=_get_run_number)
            runs = [_get_run_number(file) for file in task_files]
        else:
            runs = [1]

        for run, read_path in zip(runs, task_files):

            # Build write file name
            subject = write_path.parent.parent.name
            session = write_path.parent.name
            # Account for data without sessions
            if 'ses' not in str(session):
                subject = write_path.parent.name
                session = ''
            task = 'task-{}'.format(bandaid_es(task_name))
            run = 'run-{}'.format(str(run).zfill(3))
            write_filename = '_'.join([subject, session, task, run])
            write_stem = write_path / Path(write_filename)

            # Make corrected vhdr with original vhdr filename
            # Rename old one to .bak
            _make_temp_vhdr(read_path)
            # Load raw data
            raw = _load_raw_brainvision(read_path)

            # Logging
            ins.append(read_path)

            # Use mne_bids to write?
            if use_mne_bids:
                # Bad assumption
                write_path_mne = _trim_path_to_dir(write_path, 'rawdata')

                outs.append(_make_mne_bids_data(raw,
                                    write_path_mne,
                                    subject=_get_number(subject),
                                    session=_get_number(session),
                                    task=bandaid_es(task_name),
                                    run=_get_number(run),
                                    overwrite=overwrite,
                                    progress_bar=progress_bar))
            else:
                _make_bids_data(read_path, 
                                write_stem, 
                                raw, 
                                make_edf,
                                overwrite,
                                progress_bar)

                # Compile and write eeg metadata
                eeg_json = get_eeg_json(task_name, raw)
                _write_file(eeg_json, write_stem, 'eeg', '.json')
                channels_tsv = get_channels_tsv(raw) 
                _write_file(channels_tsv, write_stem, 'channels', '.tsv')

            # Rename original vhdr to it's original extension
            _restore_vhdr(read_path)

    make_write_log(ins, outs, 'eeg')

def bandaid_es(task_name):
    # Takes in task name as string
    # If task name is ES then return ExperienceSampling
    if task_name == 'ES':
        return 'ExperienceSampling'
    return task_name

def get_true_event_label(events, event_id):
    # If there's more than one non 255 'Stimulus' marker, take only the one
    # occuring more than once in the data

    # Find first item onset
    item_labels = [x for x in event_id.keys() if 'Stimulus' in x and 'S255' not in x]

    if len(item_labels) == 1:
        return item_labels[0]
    elif not len(item_labels):
        return None

    # If there's more than one event label
        # keep only the label occuring more than once
    d = {}
    for label in item_labels:
        count = len(events[events[:,2] == event_id[label],:])
        d[label] = count

    out = [x for x in d if d[x] > 1]

    if len(out) > 1:
        return None

    return out[0]


# --------- INTERNAL FUNCTIONS -----------

def _trim_path_to_dir(path, target_dir_name):
    '''
    Trims a pathlib.Path to end with target_dir_name

    PARAMETERS
    ---------
    path (pathlib.Path): The path to trim
    target_dir_name (str): The target path to trim at

    Returns the trimmed path as pathlib.Path
    Returns a ValueError if target_dir_name not in path
    '''
    for parent in [path] + list(path.parents):
        if parent.name == target_dir_name:
            return parent
    raise ValueError(f"Directory '{target_dir_name}' not found in path '{path}")


def _make_mne_bids_data(raw, write_path, subject, session, task, run,
                        overwrite, progress_bar):
    '''
    Write a raw BrainVision eeg file to BIDS format using mne bids

    PARAMETERS
    ---------
    raw (mne.Raw): Imported raw data object
    write_path (str): The root directory to write data to
                        Should include 'rawdata' dir
    subject (str): Subject number (just the number)
    session (str): Session number
    task (str): Task name
    run (str): Run number
    overwrite (str): Whether to overwrite existing data
    '''


    if session:
        bids_path = mne_bids.BIDSPath(subject=subject,
                                      session=session,
                                      task=task,
                                      run=run,
                                      root=write_path)
    else:
        bids_path = mne_bids.BIDSPath(subject=subject,
                                      task=task,
                                      run=run,
                                      root=write_path)

    write = 0
    if not os.path.exists(bids_path):
        write = 1
    elif overwrite:
        write = 1

    if write:
        mne_bids.write_raw_bids(raw, bids_path, overwrite=True, verbose='ERROR')

    return bids_path.fpath
    
    progress_bar.update(1)


def _get_run_number(task_file):
    '''
    Input one .eeg file
    Returns the last digits in the string
    (used as a key for sorting)
    does a smart sort (ie, handles one and two digits appropriately)
    '''
    # Splits file name (no extension) and reverses it
    s = task_file.stem.rsplit('_', -1)[::-1]
    for e in s:
        try:
            return int(e)
        except ValueError:
            pass

    raise ValueError('EEG files need a run number somewhere in the file name')


def _get_task_files(eeg_files, task_name):
    '''
    Takes as input 
        list of .eeg files as pathlib.Path objects
        the task name as string
    Returns only those eeg files that match the task name
    *assumes task is separated by _ in file name and matches exactly parent
    directory name (case insensitive)*
    '''

    out = []

    for eeg_file in eeg_files:
        params = eeg_file.stem.rsplit('_')
        for param in params:
            if param.lower() == task_name.lower():
                out.append(eeg_file)
    if not out:
        raise ValueError('Cannot parse task from EEG file name and match to directory name {}'.format(eeg_files))

    return out



def _make_temp_vhdr(read_path):
    '''
    Takes in full read path (ie, path to file and extension) of the .eeg
    file
    Returns a corrected vhdr file with the original name
    Renames the original with extension '.bak'
    '''
    # Rename original
    shutil.copy(read_path.with_suffix('.vhdr'), read_path.with_suffix('.bak'))
    with open(read_path.with_suffix('.bak'), 'r') as old_file:
        with open(read_path.with_suffix('.vhdr'), 'w') as new_file:
            for line in old_file:
                if 'DataFile' in line:
                    line = 'DataFile={}'.format(str(read_path.stem) + '.eeg\n')
                if 'MarkerFile' in line:
                    line = 'MarkerFile={}'.format(str(read_path.stem) + '.vmrk\n')
                new_file.write(line)
    new_file.close()

def _restore_vhdr(read_path):
    '''
    Takes in full read path (ie, path to file and extension) of the .eeg
    file
    Takes the .bak (temp) vhdr and restores it to the original 
    '''

    shutil.copy(read_path.with_suffix('.bak'), read_path.with_suffix('.vhdr'))
    os.remove(read_path.with_suffix('.bak'))





def _load_raw_brainvision(read_path):
    '''
    Takes in full read path as Path object
    Returns the raw data as mne object
    '''

    # Load data
    raw = mne.io.read_raw_brainvision(read_path.with_suffix('.vhdr'), 
                                      preload=False,
                                      verbose='error')

    return raw

def _make_bids_data(read_path, write_stem, raw, make_edf, overwrite, progress_bar):
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
        write_file = str(write_stem) + '_eeg.edf'
        if not overwrite and not os.path.exists(write_file):
            highlevel.write_edf(write_file,
                                raw.get_data(), 
                                signal_headers)
            print('\nSaved: {}'.format(str(write_stem) + '_eeg.edf'))
        progress_bar.update(1)

    else:
        extensions = ['.eeg', '.vhdr', '.vmrk']

        for extension in extensions:
            source_file = str(read_path.parent / read_path.stem) + extension
            write_file = str(write_stem) + '_eeg' + extension
            # i dont think this logic works
            # if overwrite is true we should write...
            if not overwrite and not os.path.exists(write_file):
                shutil.copy(source_file, write_file)
        # Update progress once per triad
        progress_bar.update(1)

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

def _get_number(x):
    '''
    Takes in a str (x) in form (eg) 'sub-001'
    Returns just the number
    '''
    return x.split('-')[-1]

