import sys
from collections import OrderedDict
import json
# Import custom modules
from helpers.validations import *
from templates.modality_agnostic import *
from templates.modality_specific import *
from helpers.make_readme import *
from helpers.create_eeg_dirs import *

'''
This script should be executed from the command line with Python.
It needs at least one argument, which is the directory of the raw data to
be converted. 
A destination directory can optionally be provided 
Otherwise, destination directory will be the dataset name (set in the
dataset_description.json) with suffix _BIDS

Right now (2023-10-12), the script assumes the first level of origin_dir
contains one sub-directory per subject (and nothing else). We'll likely
want to revise this to make it more robust.

(I need to really think about how to implement templates)
I think just do it automated as much as possible

FILES TO UPDATE MANUALLY:
    *
'''



if __name__ == '__main__':
    
    # Read command line arguments from user
    args = sys.argv[1:]
    # If no command line arguments given, quit
    # For now, restrict args to only source and dest
    if len(args) < 1 or len(args) > 2:
        print('Usage: python eeg-to-bids.py origin_dir <dest_dir>')
        sys.exit(1)

    # Import dataset description
    dataset_description = get_dataset_description()

    # Save command line arguments as separate variables
    origin_dir = args[0]
    if len(args) == 2:
        dest_dir = args[1]
    else:
        prefix = re.sub(r'[^\w]', '', dataset_description['Name'])
        dest_dir = '_'.join([prefix, 'BIDS_data'])

    # Decide whether to write raw data to .edf or just copy it as is
    make_edf = False

    # Ensure the origin directory exists
    if not os.path.exists(origin_dir):
        print('The origin path for the source data that you supplied cannot be found.')
        sys.exit(1)

    # Initialize and run basic validation
    # see helpers/validation.py
    vb = ValidateBasics(origin_dir)
    vb.confirm_subject_count()
    vb.confirm_subject_data()
    task_name = vb.confirm_task_name()

    # Create destination directory
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    
    # Compile dataset description
    # ** Could expand this to a class to handle all Level 1 files
    with open(dest_dir + '/dataset_description.json', 'w') as ff:
        json.dump(dataset_description, ff, sort_keys=False, indent=4)

    # Initialize a README
    create_readme(dest_dir, dataset_description)

    # NEED TO ADD
    # participants.tsv, participants.json, task-TASKNAME_events.json

    # Load montage
    montage = mne.channels.read_custom_montage(fname='./BC-MR3-32.bvef')

    # Iterate over subjects
    subjects = os.listdir(origin_dir)
    for subject in subjects:
        print('\nProcessing Subject {}'.format(subject))
        # Grab full file paths by run (without extensions)
        base_filenames = get_base_filenames(origin_dir, subject)
        # Make subject-specific BIDs files for each run
        for run, base_filename in enumerate(base_filenames):

            # Make bids filestem (ie, filename without suffix)
            bids_filestem = make_bids_filestem(subject,
                                               task_name,
                                               run)

            # Initialize EEG directory for a subject
            init_eeg_dir(subject, dest_dir)

            # Get raw data
            raw = load_raw_brainvision(base_filename)

            # Write / copy raw data to BIDs dir
            make_bids_data(dest_dir,
                           bids_filestem, # STILL NEED
                           raw, 
                           base_filename, 
                           subject,
                           make_edf=make_edf)

            # Make *_eeg.json and write
            #eeg_json = get_eeg_json(task_name, raw)
            #write_file(data=eeg_json, 
            #           extension='.json',
                       ## FILL IN
