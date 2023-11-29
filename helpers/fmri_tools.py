import sys
import shutil
import nibabel as nib
import os
from pathlib import Path
import copy
from tqdm import tqdm

def write_fmri(fmri_root, write_start, meta_info, overwrite, progress_bar):
    '''
    Nested within a subject-session loop
    Moves the appropriate fmri data from source to bids dest

    PARAMETERS
    -----------
    fmri_root: (pathlib.Path) path to dir containing all the fmri-scan dirs
    write_start: (pathlib.Path) path to subject and session specific area in
                               bids dir
                               eg, rawdata/sub-001/ses-001/
    meta_info: (dict) dict containing meta info on subject and session for
                      easy file naming
                      {'subject': 'sub-001', 'session': 'ses-001'}
    overwrite: (boolean) whether to overwrite existing data (with same
                         name)
    '''
    
    # Get session number
    session = int(meta_info['session'].split('-')[1])

    # Iterate over scan types
    for scan_type in ['T1w', 'B0map', 'BOLD']:

        # There's only one structural scan (session 1)
        if scan_type == 'T1w' and session > 1:
            continue

        # Extract relevant info
        key, threshold, bids_name = _get_scan_types(scan_type)

        # Find the appropriate dir
        scans = os.listdir(fmri_root)
        target_dirs = [x for x in scans if key in x]

        # Ensure there's the appropriate amount of found folders
        _error_check(target_dirs, threshold, fmri_root, scan_type)

        # Extract full file names and paths
        niis = []
        sidecars = []
        for directory in target_dirs:
            scan_root = fmri_root / Path(directory + '/NIFTI')
            files = [file for file in scan_root.iterdir() if file.is_file()]
            niis += [x for x in files if x.suffix == '.nii']
            sidecars += [x for x in files if x.suffix == '.json']

        # Make sure there's the appropriate amount of results per filetype
        for l in [niis, sidecars]:
            _error_check(l, threshold, fmri_root, scan_type)

        # Build write info
        dests = _get_dests(write_start, meta_info, scan_type, niis, sidecars)

        # Write nifti
        for nii, dest in zip(niis, dests):
            dest_path = dest.with_suffix('.nii.gz') 
            # Handle overwriting
            if not overwrite and not os.path.exists(dest_path):
                source_img = nib.load(nii)
                nib.save(source_img, dest_path)
            progress_bar.update(1)

        # Write json
        for sidecar, dest in zip(sidecars, dests):
            dest_path = dest.with_suffix('.json')
            shutil.copy(sidecar, dest_path)


def _get_dests(write_start, meta_info, scan_type, niis, sidecars):

    # Extract relevant info
    key, threshold, bids_name = _get_scan_types(scan_type)

    # Build write info
    write_path = write_start / Path(bids_name)
    subject_arg = meta_info['subject']
    session_arg = meta_info['session']

    # If anat
    if len(niis) == 1:
        write_file_stem = '_'.join([
            subject_arg,
            session_arg,
            'T1w'])
        dests = [write_path / Path(write_file_stem)]

    # If func or fmap
    # Sort niis and jsons by acquisition number
    elif len(niis) > 1:
        niis = sorted(niis, key = _get_scan_number)
        sidecars = sorted(sidecars, key = _get_scan_number)

        # suffix for fmaps is magnitude1 & 2 and phasediff (i think)
        # suffix for funcs is _bold
        if scan_type == 'B0map':
            fmap_args = ['magnitude1', 'magnitude2', 'phasediff']
            dests = []
            for fmap_arg in fmap_args:
                # Compile the file stem (file name no extension)
                write_file_stem = '_'.join([
                    subject_arg,
                    session_arg,
                    fmap_arg])

                dests.append(write_path / Path(write_file_stem))
    
        if scan_type == 'BOLD':
            dests = []
            run = 1
            last_task = ''
            for nii in niis:
                task = nii.parent.parent.name.split('_')[-1]
                if task == last_task:
                    run += 1
                last_task = copy.deepcopy(task)

                write_file_stem = '_'.join([
                    subject_arg,
                    session_arg,
                    'task-{}'.format(task),
                    'run-{}'.format(run),
                    'bold'])

                dests.append(write_path / Path(write_file_stem))

    return dests

    
def _get_scan_number(file):
    '''
    Return the scan number from a fmri full file path
    File is a pathlib.Path object
    If it's an fmap, sort first by acquisition number and then by phase
    '''
    dir_name = file.parent.parent.name
    number = dir_name.split('_')[0]
    if not 'B0map' in dir_name:
        return number
    
    # Keep last argument of file stem
    phase = file.stem.split('_')[-1]
    if phase == 'ph':
        phase = file.stem.split('_')[-2]
    # Return only the number
    phase_number = [x for x in phase if x.isdigit()][0]
    return (number, phase_number)


def _get_scan_types(scan_type):
    out = {'T1w': {}, 'B0map': {}, 'BOLD': {}}

    out['T1w']['key'] = '_T1w_'
    out['T1w']['threshold'] = 1 
    out['T1w']['bids_name'] = 'anat'

    out['B0map']['key'] = 'B0map'
    out['B0map']['threshold'] = 3
    out['B0map']['bids_name'] = 'fmap'

    out['BOLD']['key'] = '_BOLD_'
    out['BOLD']['threshold'] = None
    out['BOLD']['bids_name'] = 'func'

    return (out[scan_type]['key'],
            out[scan_type]['threshold'],
            out[scan_type]['bids_name'])
 


def _error_check(l, threshold, fmri_root, scan):
    if threshold is not None:
        if len(l) > threshold:
            raise ValueError('{} scan directory is ambiguous {} {}'.format(scan, fmri_root, l))
