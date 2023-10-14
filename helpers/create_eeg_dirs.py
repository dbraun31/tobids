import shutil
from glob import glob
import mne
import os
# see here for example: https://github.com/holgern/pyedflib
from pyedflib import highlevel

'''
Need to comment throughout
I need to determine if base_filename has a trailing /
'''


def get_base_filenames(origin_dir, subject):
    '''
    This function takes as input:
        The origin directory
        A subject id (eg, 006)
    Return the base filename (ie, file path with no extension)

    Assumes files are labeled in order of run number
    '''
    # Grab raw file names
    base_filenames = glob('/'.join([origin_dir,subject]) + '/**/*.eeg', recursive=True)
    # Sort in order of run number
    base_filenames= sorted(base_filenames)
    # Remove file extension
    base_filenames = [x.split('.')[0] for x in base_filenames]
    # Keep only unique
    base_filenames = list(set(base_filenames))

    return base_filenames

def init_eeg_dir(subject, dest_dir):
    '''
    Take as input a subject and destination directory
    Initialize the eeg directory for that subject
    '''
    to_make = '/'.join([dest_dir, 'sub-{}'.format(subject), 'eeg'])
    
    if not os.path.exists(to_make):
        os.makedirs(to_make)

def load_raw_brainvision(base_filename):
    '''
    Takes in base_filename (path to file with no extension)
    Returns the raw data as mne object
    '''

    dest_dir_path = _get_directory_path(base_filename)
    filestem = _get_filestem(base_filename)
    with open(base_filename + '.vhdr', 'r') as old_file:
        with open(dest_dir_path + 'temp.vhdr', 'w') as new_file:
            for line in old_file:
                if 'DataFile' in line:
                    line = 'DataFile={}'.format(filestem + '.eeg\n')
                if 'MarkerFile' in line:
                    line = 'MarkerFile={}'.format(filestem + '.vmrk\n')
                new_file.write(line)
    new_file.close()

    # Load data
    raw = mne.io.read_raw_brainvision(dest_dir_path + 'temp.vhdr', 
                                      preload=False,
                                      verbose='error')
    # Remove temporary vhdr
    os.remove(dest_dir_path + 'temp.vhdr')
    return raw



def make_bids_data(dest_dir, bids_filestem, raw, base_filename, subject, make_edf):
    '''
    Writes BIDs compatible data in the destination directory

    PARAMETERS
    ----------
    dest_dir: Destination directory
    bids_filestem: A BIDs compatible filestem 
                    (eg, sub-006_task-MWEEG_run-00)
    raw: mne.io.Raw
    base_filename: A path to one subject's one run with the filename
                    without an extension.
    make_edf: boolean
              whether or not to write an edf file or move the brainvision
              triplet
    '''

    # Make a full write path (without extension)
    write_path = dest_dir + '/' + 'sub-{}/'.format(subject) + 'eeg/' +\
                    bids_filestem + '_eeg'
    if make_edf:
        # Get channel names
        channel_names = raw.info['ch_names']
        sf = raw.info['sfreq']
        signal_headers = highlevel.make_signal_headers(channel_names, 
                                                       sample_frequency=sf)
        highlevel.write_edf(write_path + '.edf', 
                            raw.get_data(), 
                            signal_headers)
        print('\nSaved: {}'.format(bids_filestem + '_eeg.edf'))

    else:
        extensions = ['.eeg', '.vhdr', '.vmrk']
        filestem = _get_filestem(base_filename)

        for extension in extensions:
            source_file = base_filename + extension
            shutil.copy(source_file, write_path + extension)
            

def make_bids_filestem(subject, task_name, run):
    '''
    Produces a bids compatible filestem 
    (eg, sub-<label>_task-<TASKNAME>_run-<RUN>)

    PARAMETERS
    ----------
    subject: (string) subject number
    task_name: (string) task name
    run: (string) run number
    '''
    # Format run with three digits
    run = str(run).zfill(3)

    return '_'.join(['sub-{}'.format(subject),
                     'task-{}'.format(task_name),
                     'run-{}'.format(run)])



# --- UTILITY FUNCTIONS ---
def _get_directory_path(path):
    '''
    Takes as input either a full path or base filename
    Returns just the directory path (no filename)
    Directory path has a trailing /
    '''
    path = path.split('/')[:-1]
    return '/'.join(path) + '/'
    
def _get_filestem(path):
    '''
    Takes in a path containing file name either with or without an
    extension
    Returns just the filename without extension
    '''
    filename = path.split('/')[-1]
    if '.' in filename:
        filename = filename.split('.')[0]
    return filename






class CreateEEGDirs:
    '''
    ** Need to comment throughout
    ** Build command line argument to make converting data optional

    Think again about the scope of this...
    might leave it only as a class for importing / writing to edf
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
        signal_headers = highlevel.make_signal_headers(channel_names, 
                                                       sample_frequency=sf)
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




