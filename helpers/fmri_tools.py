import shutil
import nibabel as nib

def write_fmri(fmri_root, write_path, meta_info):
    '''
    Nested within a subject-session loop
    Moves the appropriate fmri data from source to bids dest

    PARAMETERS
    -----------
    fmri_root: (pathlib.Path) path to dir containing all the fmri-scan dirs
    write_path: (pathlib.Path) path to subject and session specific area in
                               bids dir
                               eg, /rawdata/sub-001/ses-001/
    meta_info: (dict) dict containing meta info on subject and session for
                      easy file naming
                      {'subject': 'sub-001', 'session': 'ses-001'}
    '''

    
    _write_anat(fmri_root, write_path, meta_info)



def _write_anat(fmri_root, write_path, meta_info):
    # Left off here
    # I think this works
    # still need to test in overall pipeline and comment throughout

    scans = os.listdir(fmri_root)
    t1 = [x for x in scans if 'T1w' in x]

    _error_check(t1)

    anat_root = fmri_root / Path(t1[0] + '/NIFTI')
    files = [file for file in anat_root.iterdir() if file.is_file()]
    t1 = [x for x in files if x.suffix == '.nii']
    sidecar = [x for x in files if x.suffix == '.json']

    # Make sure there's only one result per filetype
    for l in [t1, sidecar]:
        _error_check(l)


    write_path = write_path / Path('anat')

    filestem = '_'.join([meta_info['subject'], meta_info['session'], 'T1w'])

    # Write nifti
    t1_source = t1[0]
    # gzip
    t1_source_img = nib.load(t1_source)
    t1_file = filestem + '.nii.gz'
    t1_dest = write_path / Path(t1_file)
    nib.save(t1_source_img, t1_dest)
    #shutil.copy(t1_source, t1_dest)

    # Write json
    sidecar_source = sidecar[0]
    sidecar_file = filestem + '.json'
    sidecar_dest = write_path / Path(sidecar_file)
    shutil.copy(sidecar_source, sidecar_dest)


def _error_check(l):
    # if length of list is greater than 1
    if len(l) > 1:
        raise ValueError('T1w scan directory is ambiguous {}'.format(fmri_root, l))
