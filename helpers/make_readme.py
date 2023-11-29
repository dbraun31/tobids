import os
from pathlib import Path

def initialize_readme(dest_dir, dataset_description):
    '''
    Takes as input the destination directory
    Writes a mostly blank readme.md to the dir
    '''

    readme = '# README for dataset {}\n\nThorough description goes here'.format(dataset_description['Name'])
    with open(dest_dir / Path('README.md'), 'w') as ff:
        ff.write(readme)
    ff.close()

def create_readme(dest_dir, dataset_description):
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
            initialize_readme(dest_dir, dataset_description)
        else:
            os.rename(readme_dir, dest_dir + Path('README.md'))

    # If no readme already exists, create one
    else:
        initialize_readme(dest_dir, dataset_description)


