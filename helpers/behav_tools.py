import os
import sys
from pathlib import Path
import shutil
import pandas as pd
from helpers.behav_task_data import (
    gradcpt_json,
    gradcpt_headers,
    es_json
    )
import json


def write_behav(behav_files, subject, session, write_path, overwrite):
    '''
    Nested within a subject and session loop
    Moves each behavioral CSV file to its TSV BIDS dest

    PARAMETERS:
    ------------
    behav_files: list of pathlib.Path pointing to full *.csv in source dir
                assume first parent is task name
    subject: subject number string with three zero pads
    session: session number string with three zero pads
    write_path: dest/rawdata/sub-/sess-/behav as pathlib.Path
    overwrite: boolean indicating whether to overwrite existing data

    ------------

    ASSUMPTIONS:
    -----------
    1. All behavioral data and *only* behavioral data are stored as CSVs 
    2. CSVs are located directly inside a directory labeled with the
        corresponding task name
    3. CSVs are labeled such that when alphabetically sorted they will be
        in order of run number.
    '''

    es_tasks = ['es', 'experiencesampling']

    gradcpts = []
    ess = []

    # First bring in all the files to lists
    for file in behav_files:

        # If GradCPT
        inferred_task = file.parent.name.lower()
        if inferred_task == 'gradcpt':
            gradcpts.append(file)

        # If ES
        elif inferred_task in es_tasks:
            ess.append(file)

        else:
            raise ValueError('Unable to infer task name for behavioral data.')

    # Sort, assumed by run number
    gradcpts = sorted(gradcpts)
    ess = sorted(ess)

    # Prep out dir
    subject_arg = 'sub-{}'.format(subject)
    session_arg = 'sess-{}'.format(session)
        
    if not os.path.exists(write_path):
        os.makedirs(write_path)

    # Go over each run and write tsv and json to file

    # GradCPT
    for run, gradcpt in enumerate(gradcpts, start=1):
        task_arg='task-GradCPT'
        run_arg = 'run-{}'.format(str(run).zfill(3))
        out_file = Path('_'.join([subject_arg, session_arg, task_arg, run_arg,
        'behav.tsv']))

        if overwrite or not os.path.exists(out_path/out_file):
            d = pd.read_csv(gradcpt, header=None, names=gradcpt_headers)
            d.to_csv(write_path / out_file, index=False, sep='\t')

            with open(write_path / out_file.with_suffix('.json'), 'w') as file:
                json.dump(gradcpt_json, file)
            file.close()

    # ExperienceSampling
    for run, es in enumerate(ess, start=1):
        task_arg='task-ExperienceSampling'
        run_arg = 'run-{}'.format(str(run).zfill(3))
        out_file = Path('_'.join([subject_arg, session_arg, task_arg, run_arg,
        'behav.tsv']))

        if overwrite or not os.path.exists(out_path/out_file):
            d = pd.read_csv(es)
            d.to_csv(write_path / out_file, index=False, sep='\t')

            with open(write_path / out_file.with_suffix('.json'), 'w') as file:
                json.dump(es_json, file)
            file.close()




        


