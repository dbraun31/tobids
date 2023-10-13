import numpy as np
import pandas as pd
from collections import OrderedDict
from mne.channels.channels import _unit2human
from mne_bids.utils import _get_ch_type_mapping
from mne.io.pick import channel_type
from mne_bids.pick import coil_type

def get_eeg_json(task_name, raw_data):
    '''
    This function compiles the *_eeg.json file for each subject and for
    each run

    ** Come back and comment each with descriptions from docs:
    https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/03-electroencephalography.html
    '''
    raw_dict = dict(raw.info)
    data = {
        # The below fields are required
        "TaskName":task_name,
        # Taken from the BrainVision docs we were sent specific to our
        # setup
        "EEGReference":"FCz",
        "SamplingFrequency":raw.info['sfreq'], 
        "PowerLineFrequency": raw_dict.get('line_freq', 'n/a'),
        "SoftwareFilters": 'n/a',
        # The below fields are recommended
        "TaskDescription":"",
        "Instructions":"",
        "InstitutionName":"",
        "Manufacturer":"Brain Products",
        "ManufacturersModelName":"",
        "CapManufacturer":"",
        "CapManufacturersModelName":"",
        "EEGChannelCount":'',
        "EOGChannelCount":'',
        "ECGChannelCount":'',
        "EMGChannelCount":'',
        "MiscChannelCount":'',
        "TriggerChannelCount":'',
        "EEGPlacementScheme":'',
        "EEGGround":"",
        "HardwareFilters":{},
        "RecordingDuration":'',
        "RecordingType":""
    }

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

def get_coordsystem_json(raw_data):
    '''
    A *_coordsystem.json file is used to specify the fiducials, the
    location of anatomical landmarks, and the coordinate system and units
    in which the position of electrodes and landmarks is expressed. The
    *_coordsystem.json is REQUIRED if the optional *_electrodes.tsv is
    specified. If a corresponding anatomical MRI is available, the
    locations of landmarks and fiducials according to that scan should also
    be stored in the *_T1w.json file which goes alongside the MRI data.

    ** Come back and comment each with descriptions from docs:
    https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/03-electroencephalography.html
    ** I'm also omitting some of the recommended fields for now to save
    time

    See mne_bids.dig._write_coordsystem_json()
    I think this one will be complicated...


    '''

    data = OrderedDict()

    ## The following fields are required: ##
    '''
    EEG Specific Coordinate Systems

    Restricted keywords for the <CoordSysType>CoordinateSystem field in the coordsystem.json file for EEG datasets:

        CapTrak: RAS orientation and the origin approximately between LPA and RPA
        EEGLAB: ALS orientation and the origin exactly between LPA and RPA. For more information, see the EEGLAB wiki page.
        EEGLAB-HJ: ALS orientation and the origin exactly between LHJ and RHJ. For more information, see the EEGLAB wiki page.
        Any keyword from the list of Standard template identifiers: RAS orientation and the origin at the center of the gradient coil for template NifTI images
    '''
    data['EEGCoordinateSystem'] = ''

    # Must be one of: "m", "mm", "cm", "n/a"
    data['EEGCoordinateUnits'] = ''

    # This field is recommended but required if EEGCoordinateSystem is
    # 'Other'
    data['EEGCoordinateSystemDescription'] = ''


