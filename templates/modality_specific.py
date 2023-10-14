import numpy as np
import pandas as pd
from collections import OrderedDict
from mne.channels.channels import _unit2human
from mne_bids.utils import _get_ch_type_mapping
from mne.io.pick import channel_type
from mne_bids.pick import coil_type

'''
WHAT ARE THESE FUNCTIONS DOING?
They take in the necessary info. They return either a dict to be written as
json or a pandas df to be written as tsv. 
I think anything unknown from the data that I need from users, just ask the
user.
Don't worry about them having to manually edit these files, too much of a
pain.
I'll have a different function later in the pipeline that worries about
writing all these objects to file.
'''


def get_eeg_json(task_name, raw):
    '''
    This function compiles the *_eeg.json file for each subject and for
    each run

    ** Come back and comment each with descriptions from docs:
    https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/03-electroencephalography.html
    '''
    raw_dict = dict(raw.info)
    data = OrderedDict([
        # The below fields are required
        ("TaskName",task_name),
        # Taken from the BrainVision docs we were sent specific to our
        # setup
        ("EEGReference","FCz"),
        ("SamplingFrequency",raw.info['sfreq']), 
        ("PowerLineFrequency", raw_dict.get('line_freq', 'n/a')),
        ("SoftwareFilters", 'n/a'),
        # The below fields are recommended
        ("TaskDescription",""),
        ("Instructions",""),
        ("InstitutionName",""),
        ("Manufacturer","Brain Products"),
        ("ManufacturersModelName",""),
        ("CapManufacturer",""),
        ("CapManufacturersModelName",""),
        ("EEGChannelCount",''),
        ("EOGChannelCount",''),
        ("ECGChannelCount",''),
        ("EMGChannelCount",''),
        ("MiscChannelCount",''),
        ("TriggerChannelCount",''),
        ("EEGPlacementScheme",''),
        ("EEGGround",""),
        ("HardwareFilters",{}),
        ("RecordingDuration",''),
        ("RecordingType","")
         ])

def get_channels_tsv(raw):
    '''
    This function takes in the raw mne data and outputs a dataframe that
    can be written as *_channels.tsv

    *_channels.tsv is only recommended (not required)

    ** Come back and comment each with descriptions from docs:
    https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/03-electroencephalography.html
    ** See line 107 in mne_bids.write
    '''
    data = OrderedDict()
    chs = raw.info['chs']

    # Get channel type mapping from MNE to BIDs
    map_chs = _get_ch_type_mapping(fro='mne', to='bids')

    # Determine channel type and status
    # * Could also add description

    get_specific = ("mag", "ref_meg", "grad")
    ch_type, status = list(), list()
    map_chs = _get_ch_type_mapping(fro='mne', to='bids')
    for idx, ch in enumerate(raw.info['ch_names']):
        status.append('bad' if ch in raw.info['bads'] else 'good')
        _channel_type = channel_type(raw.info, idx)
        if _channel_type in get_specific:
            _channel_type = coil_type(raw.info, idx, _channel_type)
        ch_type.append(map_chs[_channel_type])

        # Determine units
        if raw._orig_units:
            units = [raw._orig_units.get(ch, "n/a") for ch in raw.ch_names]
        else:
            units = [_unit2human.get(ch_i["unit"], "n/a") for ch_i in raw.info["chs"]]
            units = [u if u not in ["NA"] else "n/a" for u in units]

    # Sampling frequencty
    sfreq = raw.info['sfreq']
    nchan = raw.info['nchan']

    ## The following fields are required: ##

    # Label of the channel.
    # Values in name MUST be unique.
    # This column must appear first in the file.
    data['name'] = raw.info['ch_names']

    # Type of channel; MUST use the channel types listed below. Note that the type MUST be in upper-case.
    # This column must appear second in the file.
    # (We'll generally want type EEG or ECG)
    
    data['type'] = ch_type

    # Physical unit of the value represented in this channel, for example, V for Volt, or fT/cm for femto Tesla per centimeter (see Units).
    # This column must appear third in the file.

    data['units'] = units

    ## The following fields are optional: ##

    data['description'] = ''
    data['sampling_frequency'] = np.full((nchan), sfreq)
    data['reference'] = ''
    data['low_cutoff'] = ''
    data['high_cutoff'] = ''
    data['notch'] = ''
    data['status'] = status
    data['status_description'] = ''

    # Keep only non-empty entries
    data = OrderedDict((key, value) for key, value in data.items() if len(value) > 1)

    return pd.DataFrame(data)


def get_electrodes_tsv(raw_data):
    '''
    This function compiles the *_electrodes.tsv file for each subject & run
    Supplying this file is optional

    This one is a doozy
    See mne.channels.montage.read_custom_montage()
        feed this the .bvef in the onedrive
    See also mne.dig._write_dig_bids()

    Oh but wait
    See mne_bids.dig._write_electrodes_tsv()
    They're just pulling from raw.info['chs'][:]['loc'][:3]

    ** Come back and comment each with descriptions from docs:
    https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/03-electroencephalography.html
    '''

    data = {}

    # Get coordinates
    coords = [x['loc'][:3] for x in raw.info['chs']]

    ## The following fields are required: ##

    data['name'] = raw.ch_names
    data['x'] = [x[0] if not np.isnan(x[0]) else 'n/a' for x in coords] 
    data['y'] = [x[1] if not np.isnan(x[1]) else 'n/a' for x in coords] 
    data['z'] = [x[2] if not np.isnan(x[2]) else 'n/a' for x in coords] 
    
    ## The following fields are recommended: ##

    data['type'] = ''
    data['material'] = ''
    data['impedance'] = [raw.impedances[x]['imp'] for x in raw.impedances]

    ## Keep only non-empty entries
    data = OrderedDict((key, value) for key, value in data.items() if len(value) > 1)

    return pd.DataFrame(data)

