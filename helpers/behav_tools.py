import os
from scipy.io import loadmat
import sys
from glob import glob
from pathlib import Path
import shutil
import re
import numpy as np
import pandas as pd
from helpers.behav_task_data import (
    gradcpt_json,
    gradcpt_headers,
    es_json
    )
import json
from mne_bids import BIDSPath


def write_behav(subject, session, seek_path, dest_path, overwrite):
    '''
    Nested within a subject and session loop
    Moves each behavioral CSV file to its events.tsv BIDS dest in func
        no current support when there's no fmri data

    PARAMETERS:
    ------------
    subject: subject number string with three zero pads
    session: session number string with three zero pads
                comes in as '-999' if only one session
    seek_path: subject/session/ as pathlib.Path
    dest_path: *_BIDS/rawdata as pathlib.Path
    overwrite: boolean indicating whether to overwrite existing data

    ------------

    ASSUMPTIONS:
    -----------
    1. All GradCPT data have "*_city_mnt_*.mat" in the filename
    2. All files named "ptbP.mat" are experience sampling data
        2a. These files have subject and run number in their path like 
            "sub-\d+" and "[Rr]un_\d+"
    3. Any CSV files without "*_city_mtn_*.mat" in the name are experience
        sampling data
    4. The non ptbP.mat data will, when sorted, be in order of run number.
    5. There will be either ptbP.mat or non *_city_mtn_*.csv experience
        sampling data, not both
    '''


    # IO
    ptbps = glob(str(seek_path / Path('**/ptbP.mat')), recursive=True)
    ptbps = [Path(x) for x in ptbps]
    ESs = glob(str(seek_path / Path('**/*.csv')), recursive=True)
    ESs = [x for x in ESs if '_city_mtn_' not in x]
    ESs = [Path(x) for x in ESs]
    if ESs:
        raise ValueError('tobids is not currently configured to handle\
        behavioral data from the eeg-fmri study')
    gradcpts = glob(str(seek_path / Path('**/*_city_mnt_*.mat')), recursive=True)
    gradcpts = [Path(x) for x in gradcpts]

    out_bids = BIDSPath(subject=subject,
                        suffix='events',
                        extension='.tsv',
                        datatype='func',
                        root=dest_path,
                        check=False)

    # Update subject and session information
    ses_string = ''
    if session != '-999':
        out_bids.session = session
        ses_string = 'ses-{}'.format(session)

    sub_string = 'sub-{}'.format(subject)


    # GradCPT
    gradcpts = _sort_by_run(gradcpts)
    for run, gradcpt in enumerate(gradcpts, start=1):
        mat = loadmat(gradcpt)
        d = _format_gradcpt(mat, gradcpt_headers)

        # Out dir
        out_bids.task = 'GradCPT'
        out_bids.run = str(run).zfill(3)
        out_bids.extension = '.tsv'
        
        if not os.path.exists(out_bids.fpath.parent):
            os.makedirs(out_bids.fpath.parent)

        if overwrite or not os.path.exists(out_bids.fpath):
            # Write tsv
            d.to_csv(out_bids.fpath, index=False, sep='\t')

        # Write json
        out_bids.update(extension='.json')
        if overwrite or not os.path.exists(out_bids.fpath):
            with open(out_bids.fpath, 'w') as file:
                json.dump(gradcpt_json, file, indent=4)
            file.close()

    # ptbPs
    ptbps = _sort_by_run(ptbps)
    for run, ptbp in enumerate(ptbps, start=1):

        # Convert path to data frame
        d = _format_ptbp(ptbp)

        # Out dir
        out_bids.task = 'ExperienceSampling'
        out_bids.run = str(run).zfill(3)
        out_bids.extension = '.tsv'
        if not os.path.exists(out_bids.fpath.parent):
            os.makedirs(out_bids.fpath.parent)

        # Write tsv
        if overwrite or not os.path.exists(out_bids.fpath):
            d.to_csv(out_bids.fpath, index=False, sep='\t')
        # Write json
        out_bids.extension = '.json'
        if overwrite or not os.path.exists(out_bids.fpath):
            with open(out_bids.fpath, 'w') as file:
                json.dump(es_json, file, indent=4)
            file.close()


def _extract_run(path):
    # Looks for a run-\d+ arg somewhere in the path
    result = re.findall('[Rr]un[-_](\d+)', str(path))
    if not result:
        return None

    result = [int(x) for x in result]
    all_equal = all(x == result[0] for x in result)

    if not all_equal:
        raise ValueError('Run number is ambiguous for {}'.format(path))

    return result[0]


def _sort_by_run(paths):
    # Take in list of paths
    # Try to extract run numbers from paths
    # Sort them by run numbers if run numbers are obtained
    # Otherwise, sort by default
        # ** BIG ASSUMPTION ** #

    runs = [_extract_run(x) for x in paths]
    if any(x is None for x in runs):
        paths = sorted(paths)
    else:
        paths = sorted(paths, key=_extract_run)

    return paths

def _format_gradcpt(mat, gradcpt_headers):
    # Takes in the mat data
    # Returns out pd df with onset and duration locked to fmri start time

    raw_onsets = mat['data'][:, 8]
    starttime = mat['starttime']
    onsets = (raw_onsets - starttime)[0]
    durations = np.diff(onsets)
    durations = np.append(durations, np.NaN)
    d = pd.DataFrame(mat['response'], columns=gradcpt_headers)
    d.insert(0, 'onset', onsets)
    d.insert(1, 'duration', durations)

    return d


def _format_ptbp(ptbp):
    # Takes in ptbp path as Path
    # Returns formatted ES data locked to scan start

    trigger_codes =  {1: 'brain', 2: 'timeout'}

    # Get triggers
    dunderp = glob(str(Path(ptbp.parent) / Path('*_P.mat')))[0]
    dunderp_mat = loadmat(dunderp)
    triggers_full = dunderp_mat['eventType'][0]  
    trigger_idxs = np.where(np.isin(triggers_full, [1, 2]))[0]
    trigger_onsets = (trigger_idxs + 1) * 2
    triggers = triggers_full[trigger_idxs]
    triggers = np.array([trigger_codes[x] for x in triggers])
    trial = np.array(range(1, len(triggers)+1))
    triggers = pd.DataFrame(np.column_stack((trial, trigger_onsets,
                                             triggers)),
                            columns=['trial', 'trigger_onset', 'event_type'])
    triggers[['trial', 'trigger_onset']] = triggers[['trial', 'trigger_onset']].astype('int64')

    # Extract ES data
    ptbp_mat = loadmat(ptbp)
    names = ptbp_mat['Task']['responses'][0,0].dtype.names
    data = ptbp_mat['Task']['responses'][0,0][0,0]
    d = {}
    for name, values in zip(names, data):
        pred = ''
        if '_' not in name:
            pred = '_response'
        d[name + pred] = [x[0][0] for x in values[0]]
    d = pd.DataFrame(d)
    d.insert(0, 'trial', range(1, d.shape[0]+1))

    # Reshape
    d = pd.melt(d, id_vars=['trial'], value_vars=d.columns.drop('trial'),
            var_name='var', value_name='value')
    d[['item', 'metric']] = d['var'].str.split('_', expand=True)
    d = d.drop('var', axis=1)
    d = d.pivot(index=['trial', 'item'], columns='metric', values='value').reset_index()
    d = d.sort_values(by=['trial', 'onset'])
    d.rename(columns={'onset': 'onset_relative', 'offset': 'offset_relative'}, inplace=True)

    # Join ES and triggers
    d = pd.merge(d, triggers, on='trial', how='left')

    # Apply transform
    # Double check with Aaron that this should be addition
    d.insert(0, 'onset', d['trigger_onset'] + d['onset_relative'])
    d.insert(1, 'offset', d['trigger_onset'] + d['offset_relative'])

    d.insert(1, 'duration', d['offset'] - d['onset'])
    d = d.drop(columns=['offset_relative', 'onset_relative', 'trigger_onset'])

    return d
