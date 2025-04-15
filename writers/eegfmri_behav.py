# Script dedicated to syncing time stamps from eeg behav data to scan start


from pathlib import Path
import mne
import pandas as pd
from writers.eeg_tools import get_true_event_label
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
    d.sort_values(by = ['trial', 'onset_original'], inplace=True)

    return d


def get_eegfmri_behav(vhdr_path, behav_path, args):
    '''
    Takes in a vmrk file
    item_order is a string of item labels in order of onset
    Extracts fMRI synched onsets labeled by item
    Overwrites onsets in behav data
    ** Only deals with ES data **
    '''

    # Get item order
    behav = pd.read_csv(behav_path)
    item_order = [x.replace('_response', '') for x in behav.columns if '_response' in x]
    behav = _reshape_behav(behav)
    message = (f'Problem inferring EEG timestamp for ES '
                     f"item for subject {args['subject']}, session"
                     f" {args['session']}, run {args['run']}.")

    # Item onset in behavioral time
    first_item_behav = behav['onset_original'].to_numpy()[0]

    # Import eeg
    raw = mne.io.read_raw_brainvision(vhdr_path)

    # --- FIND SCAN START IN EEG TIME --- #
    events, event_id = mne.events_from_annotations(raw)
    tr_label = [x for x in event_id.keys() if 'T  1' in x]

    if not len(tr_label):
        first_item_fmri = np.nan
        scan_start_eeg = np.nan
    else:
        tr_number = event_id[tr_label[0]]
        scan_start_eeg = events[events[:, 2] == tr_number, :][0][0] / raw.info['sfreq']


    # --- FIND ITEM START IN EEG TIME --- #
    item_label = get_true_event_label(events, event_id, task='ExperienceSampling')

    # If cant find a unique item label
    if item_label is None or item_label == '-9999':
        print(f'Event ID: {event_id}')
        raise ValueError(message)

    item_number = event_id[item_label]
    first_stims = events[events[:,2] == item_number][:, 0][:3] / raw.info['sfreq']
    first_durations = np.diff(first_stims)
    if not len(first_durations):
        raise ValueError(message)
    if first_durations[0] < 12.5:
        first_item_idx = 0
    elif first_durations[1] < 12.5:
        first_item_idx = 1
    else:
        raise ValueError(f'Problem inferring EEG timestamp for first ES '
                         f"item for subject {args['subject']}, session"
                         f" {args['session']}, run {args['run']}.")
    first_item_eeg = first_stims[first_item_idx]


    # --- FIND ITEM START IN FMRI TIME --- #
    first_item_fmri = first_item_eeg - scan_start_eeg


    out = {}
    item_onsets = {'eeg': first_item_eeg, 'fmri': first_item_fmri}
    modalities = ['eeg', 'fmri']

    for modality in modalities:
        # Make EEG timelocked data
        order = ['onset', 'duration', 'offset', 'trial', 'item', 'RT', 'response']
        t = behav.copy()

        # Control for missing TR markers in EEG data
        if item_onsets[modality] is np.nan:
            t['onset'] = np.nan
            t['offset'] = np.nan
            t = t.sort_values(by=['trial'])
        else:
            shift = first_item_behav - item_onsets[modality]
            t['onset'] = t['onset_original'] - shift
            t['offset'] = t['onset'] + t['duration']
            t = t.sort_values(by=['trial', 'onset'])
        t.drop(['onset_original'], axis = 1, inplace=True)
        t = t[order]
        t = t.reset_index()
        t.drop(['index'], axis=1, inplace=True)
        out[modality] = t
    
    return out['eeg'], out['fmri']

