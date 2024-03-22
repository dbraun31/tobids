# Dave Braun (2023)

from bids_validator import BIDSValidator
from glob import glob
import os
import re
import sys
from pathlib import Path
from helpers.fmri_tools import get_fmri_root

class ValidateBasics:
    '''
    A class of functions for validating the basics of the raw data, such as the
    presence of .eeg, .vhdr, and .vmrk data, and validating the task name, among
    other basics.
    '''

    def __init__(self, origin_dir):
        # Initialize the class
        self.origin_dir = origin_dir

    def confirm_subject_count(self):
        '''
        Takes as input origin directory
        Counts number of subjects (assumed to be number of subdirectories)
        Confirms with user
        Returns sample size
        '''
        # Import all first-level dirs
        dirs = [d for d in os.listdir(self.origin_dir) if os.path.isdir(self.origin_dir/ Path(d))]

        # Only keep dir if there's a number in it
        dirs = [d for d in dirs if any(char.isdigit() for char in d)]
        N = len(dirs)
        response = ''

        while response not in ['y', 'n']:
            response = input("\nI'm counting {} subjects in this directory; does that seem right? [y/n] ".format(N)).lower()
        if response == 'n':
            print('\nPlease inspect your source directory and try running the script again')
            sys.exit(1)
            
        self.N = N


    def confirm_subject_data(self):
        '''
        Takes as input origin directory
        Checks to ensure that the three main data types are present for each
        subject
        Quits the script if any are missing (but this should be updated to just
        drop the subject)
        '''
        # Import all first-level dirs
        dirs = [d for d in os.listdir(self.origin_dir) if os.path.isdir(self.origin_dir/ Path(d))]

        # Only keep dir if there's a number in it
        subject_dirs = [d for d in dirs if any(char.isdigit() for char in d)]

        for subject_dir in subject_dirs:
            subject = subject_dir.split('/')[-1]
            path = str(self.origin_dir / Path(subject_dir))
            eeg = glob(path + '/**/*.eeg', recursive=True)
            vhdr = glob(path + '/**/*.vhdr', recursive=True)
            vmrk = glob(path + '/**/*.vmrk', recursive=True)
            nii = glob(path + '/**/*.nii', recursive=True)
            if not eeg and not vhdr and not vmrk and not nii:
                raise ValueError('Subject {} has no eeg or fMRI data. Check source.'.format(subject))

        self.subject_data_present = 'Yes'



def final_validation(dest_dir):
    '''
    This function returns a score of the percentage of files in the final
    directory that are BIDS compatible.
    '''
    file_paths = []

    for root, dirs, files in os.walk(dest_dir):
        if files:
            root_chop = 1
            # Take out 'rawdata' dir if its there
            if 'rawdata' in root:
                root_chop = 2
            root = '/'.join(root.split('/')[root_chop:])
            for file in files:
                file_paths.append('/' + os.path.join(root, file))

    validator = BIDSValidator()

    result = 0
    bad_files = []

    for path in file_paths:
        if validator.is_bids(path):
            result += 1
        else:
            bad_files.append(path)

    score = round((result / len(file_paths))*100, 2)
    print("\nFinal validation of output directory.\n{}% of files in the output directory are BIDs compatible.".format(score))
    if bad_files:
        print('\n\n')
        print('Here are the incompatible files:')
        for file in bad_files:
            print(file)


def validate_task_names(subjects, origin_path):
    # Subjects comes in as list of dicts

    #  -- Try to first infer tasks from eeg data -- #

    tasks = []
    tasks = glob('{}/**/*.eeg'.format(origin_path), recursive=True)
    #for subject in subject_numbers:
        #tasks += glob('**/{}/**/*.eeg'.format(subject), recursive=True)
    tasks = [Path(x).parent.name for x in tasks]

    # -- If no eeg data, infer tasks from fmri data -- #
    if not tasks:
        subject_paths = [os.path.join(origin_path, x['path']) for x in subjects]
        for subject_path in subject_paths:
            fmri_root = get_fmri_root(subject_path)
            # A whole thing to extract task names from BOLD dirs
            bold_dirs = [x for x in os.listdir(fmri_root) if 'BOLD' in x] 
            tasks = []
            for bold_dir in bold_dirs:
                arg_list = bold_dir.split('_')
                tasks.append(arg_list[arg_list.index('BOLD') + 1])

        if not tasks:
            raise ValueError('Unable to infer task names.')


    response = ''
    while response != 'y':
        response = input('\n\nAre these the task names: {}? (y/n) '.format(str(set(tasks))))
        response = response.strip().lower()
        if response == 'n':
            raise ValueError('\n\nCheck directory structure. Directories one level above *.eeg data need to be named according to the corresponding task. Aborting.')
	
