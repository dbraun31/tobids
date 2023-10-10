import mne

file = 'MW_EEG_02_00.vhdr'


# mne website said to keep preload false...
eeg = mne.io.read_raw_brainvision(file, preload=True, verbose='error')

montage = eeg.get_montage()
montage.get_positions()

