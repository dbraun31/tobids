import os 
from scipy.io import loadmat
import sys
from glob import glob
import mne
import warnings
from pathlib import Path
import shutil
import re
import numpy as np
import pandas as pd
from writers.eeg_tools import get_true_event_label
from helpers.metadata import make_write_log
from helpers.behav_task_data import (
    gradcpt_json,
    gradcpt_headers,
    es_json
)
from writers.eegfmri_behav import get_eegfmri_behav
import json
from mne_bids import BIDSPath


def write_behav(subject, session, seek_path, dest_path, overwrite, eeg, fmri):
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
    eeg (boolean): Whether or not there is EEG data
    fmri (boolean): Whether or not there is fMRI data

    ------------

    ASSUMPTIONS:
    -----------
    1. All GradCPT data have "*_city_mnt_*.mat" in the filename
    2. All files named "ptbP.mat" are experience sampling data 
        (these only come from rt-fmri)
        2a. These files have subject and run number in their path like 
            "sub-\d+" and "[Rr]un_\d+"
    3. Any CSV files without "*_city_mtn_*.mat" in the name are experience
        sampling data
    4. The non ptbP.mat data will, when sorted, be in order of run number.
    5. There will be either ptbP.mat or non *_city_mtn_*.csv experience
        sampling data, not both

    If EEG data is present, this function will do some gnarlie processing
    to align clocks for EEG and fMRI due to a recording failure specific to
    EEG-fMRI...
    '''

    # Find all existing *_events in EEG data and delete
    path = BIDSPath(subject = subject,
                    datatype = 'eeg',
                    suffix = 'events',
                    extension = '.tsv',
                    root = dest_path / Path('rawdata'))
    if session != '-999':
        path.session = session
    events = glob(str(path.fpath.parent / Path('*events*')))
    for event in events:
        os.remove(event)


   # IO
    ptbps = glob(str(seek_path / Path('**/*ptbP.mat')), recursive=True)
    ptbps = [(Path(x), 'ptbp') for x in ptbps]
    ESs = glob(str(seek_path / Path('**/*.csv')), recursive=True)
    ESs = [x for x in ESs if '_city_mnt_' not in x]
    ESs = [(Path(x), 'csv') for x in ESs]
    ESs = ptbps + ESs

    gradcpts = glob(str(seek_path / Path('**/*_city_mnt_*.mat')), recursive=True)
    gradcpts = [(Path(x), 'gradcpt') for x in gradcpts]

    out_bids = BIDSPath(subject=subject,
                        suffix='events',
                        extension='.tsv',
                        root=dest_path,
                        check=False)
    # For logging
    ins = []    
    outs = []

    # Update subject and session information
    ses_string = ''
    if session != '-999':
        out_bids.session = session
        ses_string = 'ses-{}'.format(session)

    sub_string = 'sub-{}'.format(subject)

    # Make compact dict of args
    args = {'subject': subject,
            'session': session,
            'dest_path': dest_path}

    _validate_not_identical(gradcpts + ESs)

    # GradCPT
    gradcpts = _sort_by_run(gradcpts)
    for run, gradcpt in enumerate(gradcpts, start=1):
        # gradcpt is (path, 'type')
        
        args['run'] = str(run).zfill(3)
        mat = loadmat(gradcpt[0])
        d_eeg, d_fmri = _format_gradcpt(mat, gradcpt_headers, args, eeg)

        # Out dir
        out_bids.task = 'GradCPT'
        out_bids.run = str(run).zfill(3)
        datatypes = ['eeg', 'func']

        # Iterate over EEG/fMRI modalities
        # (Modality here just refers to which clock the behavioral data is
        # synced to)
        for d, datatype in zip([d_eeg, d_fmri], datatypes):
            
            if d is None:
                continue

            out_bids.datatype = datatype
            out_bids.update(extension = '.tsv')

            if not os.path.exists(out_bids.fpath.parent):
                os.makedirs(out_bids.fpath.parent)

            # Skip if exists and overwrite=False
            if os.path.exists(out_bids.fpath) and not overwrite:
                continue

            # Write tsv
            d.to_csv(out_bids.fpath, index=False, sep='\t')

            # Logging
            ins.append(gradcpt[0])
            outs.append(out_bids.fpath)

            # Write json
            out_bids.update(extension='.json')
            with open(out_bids.fpath, 'w') as file:
                json.dump(gradcpt_json, file, indent=4)
            file.close()

    # ESs
    # Assuming CSV or ptbp
    # Structure: (data, 'csv' or 'ptbp')
    ESs = _sort_by_run(ESs)
    for run, es in enumerate(ESs, start=1):
        run = str(run).zfill(3)
        args['run'] = run

        # Convert path to data frame
        if es[1] == 'ptbp':
            # Assuming this is fMRI only data
            d = _format_ptbp(es[0], args)
            d_hold = {'func': d}
        elif es[1] == 'csv':
            # Assuming this is EEG-fMRI ES data
            # Should add some logic down in _format_es somewhere to check
            # whether it's EEG, fMRI, or both
            d_eeg, d_fmri = _format_es(es[0], args, dest_path)
            d_hold = {'eeg': d_eeg, 'func': d_fmri}
        else:
            raise ValueError('Unable to infer ExperienceSampling data type')

        # Out dir
        out_bids.task = 'ExperienceSampling'
        out_bids.run = run
        
        for datatype in d_hold.keys():
            out_bids.extension = '.tsv'
            out_bids.datatype = datatype

            if os.path.exists(out_bids.fpath) and not overwrite:
                continue

            if not os.path.exists(out_bids.fpath.parent):
                os.makedirs(out_bids.fpath.parent)

            # Write tsv
            d_hold[datatype].to_csv(out_bids.fpath, index=False, sep='\t')

            # Logging
            ins.append(es[0])
            outs.append(out_bids.fpath)

            # Write json
            out_bids.extension = '.json'
            with open(out_bids.fpath, 'w') as file:
                json.dump(es_json, file, indent=4)
            file.close()


    # Log writing
    if all([ins, outs]):
        make_write_log(ins, outs, 'behav')


def _validate_not_identical(paths):
    '''
    Validate that the filenames for each task are distince
    paths is a list of (Path, 'task')
    '''

    ref = {}

    # Loop over paths
    for path in paths:
        # If task not in dict, add it
        if path[1] not in ref:
            ref[path[1]] = [path[0].name]
        # Otherwise
        else:
            # See if the path is already in the list
            if path[0].name not in ref[path[1]]:
                # Add it if not
                ref[path[1]].append(path[0].name)

            # If it is, it's duplicate. Throw error.
            else:
                raise ValueError('Behavioral file names must be distinct\n'
                                 f'Duplicate: {path[0].name}')


def _extract_run(path):
    '''
    Looks for a run-\d+ arg somewhere in the path
    path is a (path, 'type') tuple
    '''
    
    result = re.findall('[Rr]un[-_](\d+)', str(path[0]))
    if not result:
        return None

    result = [int(x) for x in result]
    all_equal = all(x == result[0] for x in result)

    if not all_equal:
        raise ValueError('Run number is ambiguous for {}'.format(path))

    return result[0]


def _sort_by_run(paths):
    '''
     Take in list of (path, 'type') tuples
     Try to extract run numbers from paths
     Sort them by run numbers if run numbers are obtained
     Otherwise, sort by default
         ** BIG ASSUMPTION ** #
     '''

    runs = [_extract_run(x) for x in paths]
    if any(x is None for x in runs):
        paths = sorted(paths, key=lambda x: x[0])
    else:
        paths = sorted(paths, key=_extract_run)

    return paths

def _format_gradcpt(mat, gradcpt_headers, args, eeg):
    '''
    Takes in the mat data
    Returns out pd df with onset and duration locked to fmri start time

    eeg=True means there's EEG data
    and the protocol for eeg=True is incredibly specific to the EEG-fMRI
    experiment, where clock recording got messed up, and I'm jumping
    through crazy hoops to correct it. My condolences to whatever poor
    soul is trying to parse what's happening below.
    '''

    # If dealing with rt-fmri
    if not eeg:
        d_fmri = pd.DataFrame(mat['response'], columns = gradcpt_headers)
        starttime = mat['starttime'][0][0]
        onsets = d_fmri['timestamp'] - starttime
        # Pad durations with the first onset
        durations = np.concatenate([np.array([onsets[0]]), np.diff(onsets)])
        d_fmri.insert(0, 'onset', onsets)
        d_fmri.insert(1, 'duration', durations)

        return None, d_fmri

    # If dealing with eeg-fmri data
    if eeg:
        # We need to do crazy clock syncing because I think something
        # didn't record correctly in the matlab file

        # Get eeg data
        eeg_path = BIDSPath(subject = args['subject'],
                            run = args['run'],
                            task = 'GradCPT',
                            suffix = 'eeg',
                            datatype = 'eeg',
                            extension = '.vhdr',
                            root = args['dest_path'])

        if args['session'] != '-999':
            eeg_path.session = args['session']

        raw = mne.io.read_raw_brainvision(eeg_path.fpath)
        events, event_id = mne.events_from_annotations(raw)
        raw_onsets = mat['data'][:, 8]

        # Extract event onset label from EEG data
        stim_label = get_true_event_label(events, event_id, task='GradCPT')

        # If no event labels are found, fill in NAs
        if stim_label is None:
            message = (f"Ambiguous event labels in GradCPT.\n"
                       f"Subject {args['subject']} session {args['session']} "
                       f"run {args['run']}\n"
                       f"event_id: {event_id}"
                       "\nFilling in NAs")
            print('\n', message, '\n')
            d_eeg = pd.DataFrame(mat['response'], columns=gradcpt_headers)
            d_eeg.insert(0, 'onset', np.nan)
            d_eeg.insert(1, 'duration', np.nan)

            # Use starttime to compute fmri data
            d_fmri = _starttime_resort(mat, gradcpt_headers)

            return d_eeg, d_fmri


        d_eeg, gcpt_start_e = _format_gradcpt_eeg(stim_label, events, event_id, raw, raw_onsets, mat)
        d_fmri = _format_gradcpt_fmri(stim_label, events, event_id, raw, raw_onsets, gcpt_start_e, mat)

        return d_eeg, d_fmri

def _format_gradcpt_eeg(stim_label, events, event_id, raw, raw_onsets, mat):
    '''
    Format gradcpt data timelocked to EEG start
    '''

    # Get GradCPT onset in EEG time
    avg_duration = np.diff(raw_onsets).mean()
    gcpt_end_b = raw_onsets[-1] + avg_duration # Find last trial *offset*
    gcpt_duration_b = gcpt_end_b - raw_onsets[0]
    stim_numeric = event_id[stim_label]
    gcpt_end_e = events[events[:,2]==stim_numeric,:][:,0][1] / raw.info['sfreq']
    gcpt_start_e = gcpt_end_e - gcpt_duration_b

    return _make_df(raw_onsets, gcpt_start_e, mat), gcpt_start_e

def _format_gradcpt_fmri(stim_label, events, event_id, raw, raw_onsets, gcpt_start_e, mat):
    '''
    Format gradcpt data timelocked to fMRI start
    *Not* using starttime var
    Using EEG markers
    '''
    # Get gradcpt start in fMRI time
    stim_numeric = event_id[stim_label]
    fmri_onset_e = events[events[:,2]==stim_numeric,:][:,0][0] / raw.info['sfreq']
    gcpt_start_f = gcpt_start_e - fmri_onset_e


    return _make_df(raw_onsets, gcpt_start_f, mat)


def _make_df(raw_onsets, task_start_m, mat):
    '''
    Compute a DF for EEG or fMRI relative to that clock
    task_start_m is the start of the task in the relevant data modality
    '''
    # Compute shift and make df
    shift =  raw_onsets[0] - task_start_m
    onsets = raw_onsets - shift
    durations = np.diff(onsets)
    durations = np.append(durations, np.NaN)
    d = pd.DataFrame(mat['response'], columns=gradcpt_headers)
    d.insert(0, 'onset', onsets)
    d.insert(1, 'duration', durations)

    return d


def _starttime_resort(mat, gradcpt_headers):
    '''
    If no reliable EEG events can be found, fill in the GradCPT fMRI timing
    using the 'starttime' var in the matlab data
    '''

    # Make fmri data
    raw_onsets = mat['data'][:, 8]
    starttime = mat['starttime']
    onsets = (raw_onsets - starttime)[0] + 20 # Add 20 s constant
    durations = np.diff(onsets)
    durations = np.append(durations, np.NaN)
    d_fmri = pd.DataFrame(mat['response'], columns=gradcpt_headers)
    d_fmri.insert(0, 'onset', onsets)
    d_fmri.insert(1, 'duration', durations)

    return d_fmri



def _get_stim_label(event_id):
    '''
    Get the stimulus label from eeg event labels associated with stimulus
    onset
    Assumes it has the word 'Stimulus' and not '255'
    '''
    labels = list(event_id.keys())
    for label in labels:
        if 'Stimulus' in label and '255' not in label:
            return label
    return None

def _format_ptbp(ptbp, args):
    '''
    Takes in ptbp path as Path
    Returns formatted ES data locked to scan start
    '''

    trigger_codes =  {1: 'brain', 2: 'timeout'}

    # Get triggers
    sub_twopad = str(int(args['subject'])).zfill(2) 
    run_zeropad = str(int(args['run']))
    underp_path = ptbp.parent / Path(f'../P/sub-{sub_twopad}_{run_zeropad}_P.mat')
    underp_mat = loadmat(str(underp_path))
    triggers_full = underp_mat['eventType'][0]  
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


def _format_es(behav_path, args, dest_path):
    '''
    es is path to behav data
    meta info is dict with keys subject, session, run as three digit zero
    pads
    '''

    # Need to track down the vmrk (going to get from already converted BIDS data)

    bids_dest = BIDSPath(
                    subject = args['subject'],
                    session = args['session'],
                    task = 'ExperienceSampling',
                    run = args['run'],
                    suffix = 'eeg',
                    extension = '.vhdr',
                    datatype = 'eeg',
                    root = args['dest_path'])

    vhdr_path = bids_dest.fpath

    d_eeg, d_fmri = get_eegfmri_behav(vhdr_path, behav_path, args)

    return d_eeg, d_fmri


