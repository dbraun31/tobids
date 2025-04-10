import sys
import shutil
import nibabel as nib
import re
import os
import pickle
from pathlib import Path
import copy
from tqdm import tqdm
from glob import glob
import os
import numpy as np
from helpers.metadata import make_write_log

def write_fmri(fmri_root, write_start, meta_info, overwrite, progress_bar):
    '''
    Nested within a subject-session loop
    Moves the appropriate fmri data from source to bids dest

    PARAMETERS
    -----------
    fmri_root: (pathlib.Path) path to dir containing all the fmri-scan dirs
                eg, rt-fmri/sub-11/XNAT_fMRI
    write_start: (pathlib.Path) path to subject and session specific area in
                               bids dir
                               eg, rt-fmri_BIDS/rawdata/sub-001/ses-001/
    meta_info: (dict) dict containing meta info on subject and session for
                      easy file naming
                      {'subject': 'sub-001', 'session': 'ses-001'}
                      or
                      {'subject': 'sub-001', 'session': '.'}
    overwrite: (boolean) whether to overwrite existing data (with same
                         name)
    '''

    # Logging
    outs = []
    ins = []

    # Get session number
    # Session is empty string if only one session
    if meta_info['session'] != '.':
        session = int(meta_info['session'].split('-')[1])
    else:
        meta_info['session'] = ''
        session = ''

    # Iterate over scan types
    for scan_type in ['T1w', 'B0map', 'BOLD']:

        # There's only one structural scan (session 1)
        if scan_type == 'T1w' and session and session > 1:
            continue

        # Extract relevant info
        # key is eg '_T1w_'
        # bids name ['fmap', 'func', 'anat']
        # Threshold is for validating number of expected scans
        key, threshold, bids_name = _get_scan_types(scan_type)

        # Find the appropriate dir
        scans = os.listdir(fmri_root)
        target_dirs = [x for x in scans if key in x]
        # Drop hidden dirs
        target_dirs = [x for x in target_dirs if not x.startswith('.')]

        # Ensure there's the appropriate amount of found folders
        _error_check(target_dirs, threshold, fmri_root, scan_type)

        # Extract full file names and paths
        niis = []
        sidecars = []
        for directory in target_dirs:
            scan_root = fmri_root / Path(directory + '/NIFTI')
            files = [file for file in scan_root.iterdir() if not file.name.startswith('.') and file.is_file()]
            niis += [x for x in files if x.suffix == '.nii']
            sidecars += [x for x in files if x.suffix == '.json']

        # Remove new '10\d\d.nii' scans added by software update
        if scan_type == 'BOLD':
            niis, sidecars = _cut_ten_prefix(niis, sidecars)

        # Make sure there's the appropriate amount of results per filetype
        for l in [niis, sidecars]:
            _error_check(l, threshold, fmri_root, scan_type)

        # Sort lists BEFORE computing destinations
        niis = sorted(niis, key = _get_scan_number)
        sidecars = sorted(sidecars, key = _get_scan_number)

        # Build write info
        dests = _get_dests(write_start, meta_info, scan_type, niis, sidecars)

        # Write nifti
        for nii, dest in zip(niis, dests):
            dest_path = dest.with_suffix('.nii.gz') 
            # Make dir
            if not os.path.exists(dest_path.parent):
                os.makedirs(dest_path.parent)
            # Handle overwriting
            write = False
            if os.path.exists(dest_path):
                if overwrite:
                    write = True
            else:
                write = True

            if write:
                source_img = nib.load(nii)
                nib.save(source_img, dest_path)

            ins.append(nii)
            outs.append(dest_path)
            progress_bar.update(1)

        # Write json
        for sidecar, dest in zip(sidecars, dests):
            dest_path = dest.with_suffix('.json')
            shutil.copy(sidecar, dest_path)

    make_write_log(ins, outs, 'fmri')


def _get_dests(write_start, meta_info, scan_type, niis, sidecars):

    # Extract relevant info
    key, threshold, bids_name = _get_scan_types(scan_type)

    # Build write info
    write_path = write_start / Path(bids_name)
    subject_arg = meta_info['subject']
    session_arg = meta_info['session']
    prefix = [subject_arg, session_arg]
    prefix = [x for x in prefix if x]

    # If anat
    if 'T1w' in niis[0].name:
        args = prefix + ['T1w']
        write_file_stem = '_'.join(args)
        dests = [write_path / Path(write_file_stem)]

    # If func or fmap
    # Sort niis and jsons by acquisition number
    else:
        # suffix for fmaps is magnitude1 & 2 and phasediff (i think)
        # suffix for funcs is _bold
        if scan_type == 'B0map':
            fmap_args = ['magnitude1', 'magnitude2', 'phasediff']
            dests = []
            for fmap_arg in fmap_args:
                # Compile the file stem (file name no extension)
                args = prefix + [fmap_arg]
                write_file_stem = '_'.join(args)
                dests.append(write_path / Path(write_file_stem))
    
        if scan_type == 'BOLD':
            dests = []
            last_task = ''
            # Update run number based on task
            task_runs = {}
            for nii in niis:
                # Assumes task name is the parameter after BOLD
                arg_list = nii.parent.parent.name.split('_')
                # cant assume _ splitting will perfectly 
                # isolate the word BOLD
                idx = [i for i, e in enumerate(arg_list) if 'BOLD' in e][0]
                task = arg_list[idx+1]
                # Standardize ES vs. ExperienceSampling
                task = 'ExperienceSampling' if task == 'ES' else task
                if task not in task_runs:
                    task_runs[task] = 1
                else:
                    task_runs[task] += 1

                last_task = copy.deepcopy(task)

                args = prefix + ['task-{}'.format(task),
                                 'run-{}'.format(str(task_runs[task]).zfill(3)),
                                 'bold']
                write_file_stem = '_'.join(args)

                dests.append(write_path / Path(write_file_stem))

    return dests

    
def _get_scan_number(file):
    '''
    Return the scan number from a fmri full file path
    File is a pathlib.Path object
    If it's an fmap, sort first by acquisition number and then by phase
    '''
    dir_name = file.parent.parent.name
    try:
        number = int(re.search(r'(\d+)[-_]', dir_name).group(1))
    except:
        print(file)
        raise ValueError('Failed to parse run number and convert to int')
        sys.exit(1)
    if not 'B0map' in dir_name:
        return number
    
    # Keep last argument of file stem (unless it's 'ph')
    phase = file.stem.split('_')[-1]
    if phase == 'ph':
        phase = file.stem.split('_')[-2]
    # Return only the number
    phase_number = [x for x in phase if x.isdigit()][0]
    return (number, phase_number)


def _get_scan_types(scan_type):
    # Cant assume key words (ie, BOLD) 
    # will be surrounded by underscores
    out = {'T1w': {}, 'B0map': {}, 'BOLD': {}}

    out['T1w']['key'] = 'T1w'
    out['T1w']['threshold'] = 1 
    out['T1w']['bids_name'] = 'anat'

    out['B0map']['key'] = 'B0map'
    out['B0map']['threshold'] = 3
    out['B0map']['bids_name'] = 'fmap'

    out['BOLD']['key'] = 'BOLD'
    out['BOLD']['threshold'] = None
    out['BOLD']['bids_name'] = 'func'

    return (out[scan_type]['key'],
            out[scan_type]['threshold'],
            out[scan_type]['bids_name'])
 


def _error_check(l, threshold, fmri_root, scan):
    if threshold is not None:
        if len(l) > threshold:
            raise ValueError('{} scan directory is ambiguous {} {}'.format(scan, fmri_root, l))

def get_fmri_root(seek_path):
    # Returns the fmri root directory 
    # Seek path is origin_path / subject / session
    # Raises an error if it doesn't find exactly one dir

    keywords = ['BOLD', 'AAHScout', 'Localizer', 'B0map']

    founds = []

    for dirpath, dirnames, filenames in os.walk(seek_path):
        hits = 0
        for keyword in keywords:
            if any(keyword in x for x in dirnames):
                hits += 1
        if hits == len(keywords):
            founds.append(dirpath)

    if len(founds) != 1:
        print('Seek path: {}\n'.format(seek_path))
        raise ValueError('Unable to infer fMRI root directory. Expected to find 1 root directory but found {}'.format(len(founds)))

    for item in os.listdir(founds[0]):
        look_dir = os.path.join(founds[0], item)
        if os.path.isdir(look_dir) and 'BOLD' in item:
            niis = glob(look_dir + '/**/*.nii', recursive=True)
            if not niis:
                raise ValueError('Unable to infer fMRI root directory. No .nii file in {}'.format(look_dir))


    return founds[0]

def _cut_ten_prefix(niis, sidecars):
    # Cut out the weird 10\d\d.nii that got added by the software update

    pattern = r'.*_\d\d\.[a-z]+$'
    niis_out = []
    sidecars_out = []

    for nii, sidecar in zip(niis, sidecars):
        if re.search(pattern, nii.name) is not None:
            niis_out.append(nii)
            sidecars_out.append(sidecar)

    return niis_out, sidecars_out
