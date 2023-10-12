import pandas as pd
import mne
import scipy.io as sio

file = 'sample_data/MW_EEG_02_00.vhdr'


# mne website said to keep preload false...
eeg = mne.io.read_raw_brainvision(file, preload=False, verbose='error')

montage = eeg.get_montage()
montage.get_positions()

## gotta figure out how this works
## these files are represented as matlab 'tables', which can't be parsed by
# python =(
data = scp.loadmat('sample_data/MW_EEG_002_01_12-Jul-2023_11_11.mat')

data = pd.read_csv('behavioral_data.csv')

