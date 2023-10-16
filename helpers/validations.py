from bids_validator import BIDSValidator
from glob import glob
import os
import re
import sys

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
        N = len(os.listdir(self.origin_dir))
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
        subject_dirs = os.listdir(self.origin_dir)

        for subject_dir in subject_dirs:
            subject = subject_dir.split('/')[-1]
            path = self.origin_dir + '/' + subject_dir
            eeg = glob(path + '/**/*.eeg')
            vhdr = glob(path + '/**/*.vhdr')
            vmrk = glob(path + '/**/*.vmrk')
            if not eeg or not vhdr or not vmrk:
                raise ValueError('Subject {} is missing one or more of the data files'.format(subject))

        self.subject_data_present = 'Yes'

    def confirm_task_name(self):
        '''
        Takes as input the origin directory as a string
        Extracts task name from subject data file
        Confirms with user / asks for new name

        ** This script guesses that everything before the first digit will be
        the task name (can revisit this assumption)
        ** This script also cleans the task name such that it contains only
        A-Z characters (converts to uppercase)
        '''
        # Grab the first .eeg file
        file = glob(self.origin_dir + '/**/*.eeg', recursive=True)[0].split('/')[-1]

        # Extract task name from this file name
        # (Pulls everything before the first digit, removes underscores and
        # dashes)
        task_name_search = re.search(r'^\D+', file)

        # If we recover a potential task name from the filename
        if task_name_search:
            task_name = task_name_search.group()
            # Remove _ and -
            task_name = re.sub(r'[^a-z^A-Z]', '', task_name)
            response = ''
            # Ask if okay
            while response not in ['y', 'n']:
                response = input("\nI need a name for the task. Would you like to call the task {}? [y/n] ".format(task_name)).lower()
            # If not okay, get task name and clean string
            if response == 'n':
                task_name = ''
                while not task_name:
                    task_name = input('\nPlease enter a name for the task: ')
                task_name = re.sub(r'[^a-z^A-Z]', '', task_name)

        # If we didn't recover a potential task name, ask for one
        else:
            task_name = input('\nPlease enter a name for the task: ')
            task_name = re.sub(r'[^a-z^A-Z]', '', task_name)

        print('\nThe task will be called {}'.format(task_name.upper()))

        return task_name.upper()

    def generate_dataset_description(self):
        # see ./helpers/get_dataset_description
        return ''


def final_validation(dest_dir):
    '''
    This function returns a score of the percentage of files in the final
    directory that are BIDS compatible.
    '''
    file_paths = []

    for root, dirs, files in os.walk(dest_dir):
        root = '/'.join(root.split('/')[1:])
        for file in files:
            file_paths.append('/' + os.path.join(root, file))

    validator = BIDSValidator()

    result = 0

    for path in file_paths:
        if validator.is_bids(path):
            result += 1

    score = round((result / len(file_paths))*100, 2)
    print("\nFinal validation of output directory.\n{}% of files in the output directory are BIDs compatible.".format(score))


