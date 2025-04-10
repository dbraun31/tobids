# Script dedicated to syncing time stamps from eeg behav data to scan start


from pathlib import Path
import mne
import pandas as pd
import numpy as np
from glob import glob
import re


def _reshape_behav(behav):

    d = behav.copy()
    d['trial'] = np.arange(1, d.shape[0]+1)
    d = d.melt(id_vars=['trial'], var_name='metric', value_name='measurement')
    d[['item', 'type']] = d['metric'].str.split('_', expand=True)
    d = d.drop(columns=['metric'])
    d = d.pivot(index=['trial', 'item'], columns='type', values='measurement').reset_index()
    d['duration'] = d['offset'] - d['onset']
    d.rename(columns = {'onset': 'onset_original'}, inplace=True)

    return d


def get_eegfmri_behav(vhdr_path, behav_path, args):
    '''
    Takes in a vmrk file
    item_order is a string of item labels in order of onset
    Extracts fMRI synched onsets labeled by item
    Overwrites onsets in behav data
    '''

    # Get item order
    behav = pd.read_csv(behav_path)
    item_order = [x.replace('_response', '') for x in behav.columns if '_response' in x]
    behav = _reshape_behav(behav)

    # Import eeg
    raw = mne.io.read_raw_brainvision(vhdr_path)

    # Find scan start time
    events, event_id = mne.events_from_annotations(raw)
    tr_label = [x for x in event_id.keys() if 'T  1' in x][0]
    tr_number = event_id[tr_label]
    scan_start_s = events[events[:, 2] == tr_number, :][0][0] / raw.info['sfreq']

    # Find first item onset
    item_label = [x for x in event_id.keys() if 'Stimulus' in x and 'S255' not in x]

    # Ensure there's only one non Stimulus/ S255
    if len(item_label) > 1:
        # keep only the label occuring more than once
        item_label = _get_true_label(events, event_id, item_label)
        if not item_label:
            raise ValueError(f'Problem inferring EEG timestamp for first ES '
                             f"item for subject {args['subject']}, session"
                             f" {args['session']}, run {args['run']}.")
    else:
        item_label = item_label[0]

    item_number = event_id[item_label]
    first_stims = events[events[:,2] == item_number][:, 0][:3] / raw.info['sfreq']
    first_durations = np.diff(first_stims)
    if not len(first_durations):
        raise ValueError(f'Problem inferring EEG timestamp for first ES '
                         f"item for subject {args['subject']}, session"
                         f" {args['session']}, run {args['run']}.")
    if first_durations[0] < 12.5:
        first_item_idx = 0
    elif first_durations[1] < 12.5:
        first_item_idx = 1
    else:
        raise ValueError(f'Problem inferring EEG timestamp for first ES '
                         f"item for subject {args['subject']}, session"
                         f" {args['session']}, run {args['run']}.")
    first_item_s = first_stims[first_item_idx]

    out = {}
    offset = {'eeg': first_item_s, 'fmri': scan_start_s}
    modalities = ['eeg', 'fmri']

    for modality in modalities:
        # Make EEG timelocked data
        order = ['onset', 'duration', 'offset', 'trial', 'item', 'RT', 'response']
        shift = behav['onset_original'][0] - offset[modality]
        t = behav.copy()
        t['onset'] = t['onset_original'] - shift
        t.drop(['onset_original'], axis = 1, inplace=True)
        t['offset'] = t['onset'] + t['duration']
        t = t[order]
        t = t.sort_values(by=['trial', 'onset'])
        t = t.reset_index()
        t.drop(['index'], axis=1, inplace=True)
        out[modality] = t
    
    return out['eeg'], out['fmri']


def _get_true_label(events, event_id, item_labels):
    # If there's more than one non 255 'Stimulus' marker, take only the one
    # occuring more than once in the data

    d = {}
    for label in item_labels:
        count = len(events[events[:,2] == event_id[label],:])
        d[label] = count

    out = [x for x in d if d[x] > 1]

    if len(out) > 1:
        return None

    return out[0]



        
