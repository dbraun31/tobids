from pathlib import Path
import shutil
import os
from glob import glob
from scipy.io import loadmat
import sys
import pandas as pd

'''
A script to help converting behavioral data from mat to csv
it first crawls through the whole data dir looking for mat files
    and moves them to a 'csv' folder
then need to run a matlab script to convert
then run this script again to disperse the csvs back into the original dirs
'''



if __name__ == '__main__':
    
    args = sys.argv[1:]
    if len(args) != 1:
        print('Point to the dir containing the data')
        sys.exit(1)

    target = args[0] 

    get_mats = False
    spread_csvs = False

    if not os.path.exists('csvs'):
        os.mkdir('csvs')

    if os.path.exists('mats'):
        if os.listdir('csvs'):
            spread_csvs = True
    else:
        os.mkdir('mats')
        get_mats = True

    
    if get_mats:
        files = glob('{}/**/*.mat'.format(target), recursive=True)
        files = [Path(x) for x in files]

        for file in files:
            
            if 'Data' in file.name:
                d = loadmat(file)
                out_file = 'csvs/' + file.with_suffix('.csv').name
                pd.DataFrame(d['response']).to_csv(out_file, index=False,
                                                   header=None)

            else:
                shutil.copy(file, 'mats/' + file.name)


        print('CONVERT MATS TO CSVS WITH TABLE_TO_MAT.M')
    
    ## After ES mat files have been converted
    if spread_csvs:
        files = glob('csvs/*.csv')
        files = [Path(x) for x in files]
        out_stem = '{}/**/'.format(target)

        for file in files:
            out_filename = file.with_suffix('.mat').name
            old_file = glob(out_stem + out_filename, recursive=True)[0]
            out_path = Path(old_file).parent
            out_file = Path(file.name)
            shutil.copy(file, out_path / out_file)





            
        
