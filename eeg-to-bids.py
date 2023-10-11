import sys
from collections import OrderedDict
import json
# Import custom modules
from helpers.validations import *
from get_dataset_description import get_dataset_description

'''
This script should be executed from the command line with Python.
It needs at least one argument, which is the directory of the raw data to
be converted. 
A destination directory can optionally be provided (by default the output
will be saved to ./BIDS_data/

FILES TO UPDATE MANUALLY:
    *
'''

def initialize_readme(dest_dir):
    '''
    Takes as input the destination directory
    Writes a mostly blank readme.md to the dir
    '''

    readme = '# README for dataset {}\n\nThorough description goes here'.format(dataset_description['Name'])
    with open(dest_dir + '/README.md', 'w') as ff:
        ff.write(readme)
    ff.close()

def create_readme(dest_dir):
    '''
    Description pending.
    '''
    response = ''
    while response not in ['y', 'n']:
        response = input('\nDo you have an existing readme file? [y/n] ')
    # If a readme exists
    # Ask for the path and move to destination
    if response == 'y':
        readme_dir = input('\nPlease provide the path to the readme file: ')
        if not os.path.exists(readme_dir):
            print("Readme file doesn't exist. Initializing a blank one.")
            initialize_readme(dest_dir)
        else:
            os.rename(readme_dir, dest_dir + '/README.md')

    # If no readme already exists, create one
    else:
        initialize_readme(dest_dir)


if __name__ == '__main__':
    
    # Read command line arguments from user
    args = sys.argv[1:]
    # If no command line arguments given, quit
    # For now, restrict args to only source and dest
    if len(args) < 1 or len(args) > 2:
        print('Usage: python eeg-to-bids.py origin_dir <dest_dir>')
        sys.exit(1)

    # Save command line arguments as separate variables
    origin_dir = args[0]
    if len(args) == 2:
        dest_dir = args[1]
    else:
        dest_dir = 'BIDS_data'

    # DEV for now hard code
    origin_dir = 'sample_data'
    dest_dir = 'BIDS_data'

    # Ensure the origin directory exists
    if not os.path.exists(origin_dir):
        print('You must choose an origin directory (for the raw data you want to convert) that already exists')
        sys.exit(1)

    # Initialize and run basic validation
    # see helpers/validation.py
    vb = ValidateBasics(origin_dir)
    vb.confirm_subject_count()
    vb.confirm_subject_data()
    vb.confirm_task_name()

    # Create destination directory
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    
    # Compile dataset description
    dataset_description = get_dataset_description()
    with open(dest_dir + '/dataset_description.json', 'w') as ff:
        json.dump(dataset_description, ff, sort_keys=False, indent=4)

    # Initialize a README
    create_readme(dest_dir)
