# taken from: https://github.com/bids-standard/bids-starter-kit/blob/main/pythonCode/createBIDS_dataset_description_json.py

from collections import OrderedDict
from pathlib import Path
import pickle
import shutil
from glob import glob
import json
import os
import pandas as pd
import json

def make_write_log(ins, outs, modality):
    first_dir = outs[0].parts[0]
    write_log = {}
    name = f'{first_dir}/conversion_log_{modality}'
    if os.path.exists(name + '.pkl'):
        with open(name + '.pkl', 'rb') as file:
            write_log = pickle.load(file) 
    for i, o in zip(ins, outs):
        write_log[str(i)] = str(o)
    with open(name + '.pkl', 'wb') as file:
        pickle.dump(write_log, file)
    with open(name + '.json', 'w') as file:
        json.dump(write_log, file, indent=4)
    file.close()


def make_metadata(dest_path):
    # Produces readme, participants.tsv, participants.json,
    # dataset_description.json
    # only if they don't already exist

    # README
    text = 'General dataset information goes here.'
    filename = os.path.join(dest_path, 'README')
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            file.write(text)
        file.close()

    # Dataset description
    filename = os.path.join(dest_path, 'dataset_description.json')
    with open(filename, 'w') as file:
        file.write(str(_make_dataset_description()))
        file.close()

    # participants.json
    filename = os.path.join(dest_path, 'participants.json')
    with open(filename, 'w') as file:
        file.write(str(_make_participants_metadata()))
        file.close()

    
    # participants.tsv
    filename = os.path.join(dest_path, 'participants.tsv')
    if not os.path.exists(filename):
        subjects = glob(os.path.join(dest_path, 'sub*'))
        subjects = sorted([Path(x).name for x in subjects])
        cols = _make_participants_metadata().keys()
        t = pd.DataFrame(columns=cols)
        t['participant_id'] = subjects
        t.sort_values(by='participant_id')
        t.fillna('n/a')
        t.to_csv(filename, sep='\t', index=False)



def _make_dataset_description():
    dd = {
        "Name": " ",
        "BIDSVersion": "1.7.0",
        "DatasetType": "raw",
        "Authors": [
            "[Unspecified]"
        ]
    }

    return dd


def _make_participants_metadata():
    pm = {
        "participant_id": {
            "Description": "Unique participant identifier"
        },
        "age": {
            "Description": "Age of the participant at time of testing",
            "Units": "years"
        },
        "sex": {
            "Description": "Biological sex of the participant",
            "Levels": {
                "F": "female",
                "M": "male"
            }
        },
        "hand": {
            "Description": "Handedness of the participant",
            "Levels": {
                "R": "right",
                "L": "left",
                "A": "ambidextrous"
            }
        },
        "weight": {
            "Description": "Body weight of the participant",
            "Units": "kg"
        },
        "height": {
            "Description": "Body height of the participant",
            "Units": "m"
        }
    }
    return pm

