# Script dedicated to syncing time stamps from eeg behav data to scan start


from pathlib import Path
import pandas as pd
import numpy as np
from glob import glob
import re

def _get_events_per_probe(vmrk):
    '''
    Identify based on subject and session in path whether each probe has 13
    or 14 events
    '''

    name = Path(vmrk).name
    subject = int(re.search(r'fMRI_(\d+)', name).group(1))
    session = int(re.search(r'_(\d+)\.', name).group(1))

    if subject == 1 or (subject == 2 and session == 1):
        return 13
    return 14


def _reshape_behav(behav):

    d = behav.copy()
    d['trial'] = np.arange(1, d.shape[0]+1)
    d = d.melt(id_vars=['trial'], var_name='metric', value_name='measurement')
    d[['item', 'type']] = d['metric'].str.split('_', expand=True)
    d = d.drop(columns=['metric'])
    d = d.pivot(index=['trial', 'item'], columns='type', values='measurement').reset_index()
    d['duration'] = d['offset'] - d['onset']
    d = d.drop(columns=['onset'])

    return d


def get_eegfmri_behav(vmrk_path, behav, sfreq=5000):
    '''
    Takes in a vmrk file
    item_order is a string of item labels in order of onset
    Extracts fMRI synched onsets labeled by item
    Overwrites onsets in behav data
    '''

    # Get item order
    item_order = [x.replace('_response', '') for x in behav.columns if '_response' in x]

    # Import vmrk
    columns = ['full_marker', 'marker', 'timestamp', 'x', 'y', 'z']
    vmrk = pd.read_csv(vmrk_path, skiprows=11, header=None, names=columns)
    vmrk = vmrk[['marker', 'timestamp']].to_numpy()

    # fMRI start timestamp
    scan_start = vmrk[np.where(vmrk[:,0]=='T  1')[0][0], 1]

    # Identify stim onsets
    start_markers = ['S  1', 'S 39', 'S167']
    onsets_raw = vmrk[np.where(np.isin(vmrk[:,0], start_markers))[0],1]

    # Identify probe count
    events_per_probe = _get_events_per_probe(vmrk_path)
    n_probes = int(len(onsets_raw) / events_per_probe)

    if n_probes % 2:
        raise ValueError('Problem inferring probe count for {}'.format(vmrk))

    # Remove fixation events if present
    if events_per_probe == 14:
        yank = np.arange(0, len(onsets), 14)
        onsets_raw = np.delete(onsets_raw, yank)

    # Shift onsets to fmri scan start
    onsets = onsets_raw - scan_start

    # Convert to seconds, concatenate to item labels
    onsets = onsets / sfreq 
    trials = np.repeat(np.arange(1, n_probes+1), 13)
    items = np.column_stack((trials, item_order * n_probes))
    onsets = np.column_stack((items, onsets))
    onsets = pd.DataFrame(onsets, columns=['trial', 'item', 'onset'])
    onsets['trial'] = onsets['trial'].astype('Int64')

    # Merge with behav data
    behav = _reshape_behav(behav)
    d = pd.merge(behav, onsets, on=['trial', 'item'], how='left')
    d['offset'] = d['onset'] + d['duration']
    order = ['onset', 'duration', 'offset', 'trial', 'item', 'RT', 'response']
    d = d[order]

    # Shouldn't be strictly necessary if onset is correct.. but it's a good
    # validation
    d['item'] = pd.Categorical(d['item'], categories=item_order, ordered=True)
    d = d.sort_values(by=['trial', 'item'])

    return d


