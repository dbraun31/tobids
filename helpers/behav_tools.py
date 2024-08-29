import os
import sys
from pathlib import Path
import shutil
import numpy as np
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
    write_path: dest/rawdata/sub-/sess-/func as pathlib.Path
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
            raise ValueError('Unable to infer task name for behavioral data.\nSubject: {}\nSession: {}\nInferred task name: {}\nFile: {}.\nDirectory containing data must match: "gradcpt" or "es" / "experiencesampling".'.format(subject, session, inferred_task, file))

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
        'events.tsv']))

        if overwrite or not os.path.exists(write_path/out_file):
            d = pd.read_csv(gradcpt, header=None, names=gradcpt_headers)

            # Reformat data
            d = _reformat_gradcpt(d)

            d.to_csv(write_path / out_file, index=False, sep='\t')

            with open(write_path / out_file.with_suffix('.json'), 'w') as file:
                json.dump(gradcpt_json, file)
            file.close()

    # ExperienceSampling
    for run, es in enumerate(ess, start=1):
        task_arg='task-ExperienceSampling'
        run_arg = 'run-{}'.format(str(run).zfill(3))
        out_file = Path('_'.join([subject_arg, session_arg, task_arg, run_arg,
        'events.tsv']))

        if overwrite or not os.path.exists(write_path/out_file):
            d = pd.read_csv(es)

            # Reformat data
            d = _reformat_es(d)

            d.to_csv(write_path / out_file, index=False, sep='\t')

            with open(write_path / out_file.with_suffix('.json'), 'w') as file:
                json.dump(es_json, file)
            file.close()


def _compute_diff(row):
    '''
    Compute difference between two values only if neither of them are zero.
    '''
    current_value = row['onset']
    next_value = row['shifted']

    if current_value != 0 and next_value != 0:
        return next_value - current_value
    return np.nan

def _reformat_gradcpt(d):
    '''
    Take in raw GradCPT data and reformat to be compatible with BIDS
    ie, Columns "onset" and "duration" should be in front, followed by the
    rest.
    '''

    # Get remaining column names 
    trail_cols = [x for x in d.columns if x != 'onset']

    # Compute shift column
    d['shifted'] = d['onset'].shift(-1)

    # Take difference for non-zero values
    d['duration'] = d.apply(_compute_diff, axis=1)
    d.drop(columns=['shifted'], inplace=True)

    # Move duration and onset to front
    d = d[['onset', 'duration'] + trail_cols]

    return d


def _reformat_es(d):
    '''
    Take in raw ExperienceSampling data and reformat to be compatible with
    BIDS
    '''
    
    # temp 
    in_file = '../data_conversion/csvs/EEG-fMRI_010_V1_02_06-May-2024_15_34.csv'
    d = pd.read_csv(in_file)

    # Make probe count
    d.insert(0, 'probe_number', np.array(range(d.shape[0]))+1)

    d = pd.melt(d, id_vars=['probe_number'], var_name='variable', value_name='value')
    s = dt['variable'].str.split(pat='_', n=1, expand=True)
    d['item'] = s[0]
    d['metric'] = s[1]
    d.drop(columns=['variable'], inplace=True)
    d = d.pivot(index=['probe_number', 'item'], columns='metric',
            values='value').reset_index()
    d['duration'] = d['offset'] - d['onset']
    trail_cols = [x for x in d.columns if x not in ['onset', 'duration']]
    d = d[['onset', 'duration'] + trail_cols]

    return d
        


