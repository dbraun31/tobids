from pathlib import Path
from helpers.modality_agnostic import get_dataset_description

def parse_command_line(args):
    '''
    Takes as input command line arguments as a list of strings
    Ensures origin path is specified and valid
    Returns origin and dest as pathlib.Path
    '''
    
    # If no command line arguments given, quit
    # For now, restrict args to only source and dest
    if len(args) < 0 or len(args) > 2:
        raise ValueError('Usage: python eeg-to-bids.py origin_dir <dest_dir>')

    # Import dataset description
    dataset_description = get_dataset_description()

    # Save command line arguments as separate variables
    origin_path = Path(args[-1])
    if len(args) == 1:
        dest_path = Path(args[0])

    # If no destination path is provided
    else:
        # infer one from the dataset name
        prefix = re.sub(r'[^\w]', '', dataset_description['Name'])
        dest_path = Path('_'.join([prefix, 'BIDS_data']))

    # Ensure the origin directory exists
    if not os.path.exists(origin_dir):
        raise ValueError('The origin path for the source data that you supplied cannot be found.')

    return [origin_path, dest_path]

