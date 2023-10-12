from glob import glob
import mne
import os
# see here for example: https://github.com/holgern/pyedflib
from pyedflib import highlevel

'''
Need to comment throughout
'''


def determine_runs(origin_dir, subject):
    '''
    This function takes as input a subject id (eg, 006)
    Return the filenames (without extensions) of each run

    Assumes files are labeled in order of run number
    '''
    # Grab raw file names
    runs = glob('/'.join([origin_dir,subject]) + '/**/*.eeg', recursive=True)
    # Sort in order of run number
    runs = sorted(runs)
    # Remove file extension
    runs = [x.split('.')[0] for x in runs]

    return runs


class CreateSubjectDirs:
    '''
    dont know if it makes sense to have this be an all-purpose file maker
    or not
    i think it would be fine
    all these attributes are what i'd need to make them anyway
    '''

    def __init__(self, file_path, dest_dir, subject, task, run):
        self.file_path = file_path
        self.dest_dir = dest_dir
        self.subject = subject
        self.task = task
        self.run = run
        self.path = self._extract_path()
        self.file = self.file_path.split('/')[-1]
        self.raw = self._load_raw_data()
        self.filename = 'sub-{}_task-{}_run-{}'.format(self.subject, 
                                                          self.task, 
                                                          self.run)


    def write_edf(self):
        channel_names = self.raw.info['ch_names']
        sf = self.raw.info['sfreq']
        signal_headers = highlevel.make_signal_headers(channel_names, sample_frequency=sf)
        self._make_subject_dir()
        highlevel.write_edf(self.subject_path + '/' + self.filename + '_eeg.edf', 
                            self.raw.get_data(), 
                            signal_headers)

   # other file making functions go here... 

    def _load_raw_data(self):
        self._create_temp_vhdr()
        raw_data = mne.io.read_raw_brainvision(self.path + 'temp.vhdr', preload=False)
        # Remove temporary vhdr
        os.remove(self.path + 'temp.vhdr')
        return raw_data

    def _create_temp_vhdr(self):
        with open(self.file_path + '.vhdr', 'r') as old_file:
            with open(self.path + 'temp.vhdr', 'w') as new_file:
                for line in old_file:
                    if 'DataFile' in line:
                        line = 'DataFile={}'.format(self.file + '.eeg\n')
                    if 'MarkerFile' in line:
                        line = 'MarkerFile={}'.format(self.file + '.vmrk\n')
                    new_file.write(line)
        new_file.close()

    def _extract_path(self):
        # Get just the path (no filename)
        path = self.file_path.split('/')[:-1]
        path = '/'.join(path) + '/'
        return path

    def _make_subject_dir(self):
        self.subject_path = self.dest_dir + '/sub-' + self.subject + '/eeg'
        if not os.path.exists(self.subject_path):
            os.makedirs(self.subject_path)




