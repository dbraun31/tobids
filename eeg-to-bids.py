import sys
from helpers.validations import *




if __name__ == '__main__':
    
    # Read command line arguments from user
    args = sys.argv[1:]
    # If no command line arguments given, quit
    # For now, restrict args to only source and dest
    if len(args) != 2:
        print('Usage: python eeg-to-bids.py origin_dir dest_dir')
        sys.exit(1)

    # Save command line arguments as separate variables
    # DEV for now hard code
    origin_dir = args[0]
    dest_dir = args[1]
    origin_dir = 'sample_data'
    dest_dir = 'bids_data'

    # Ensure the origin directory exists
    if not os.path.exists(origin_dir):
        print('You must choose an origin directory (for the raw data you want to convert) that already exists')
        sys.exit(1)

    # Initialize and run basic validation
    vb = ValidateBasics(origin_dir)
    vb.confirm_subject_count()
    vb.confirm_subject_data()
    vb.confirm_task_name()


