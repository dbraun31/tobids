# ToBids

ToBids is a general Python tool developed for the [Dynamic Brain and Mind Lab](https://sites.google.com/site/aaronkucyi)
to convert raw neuro data to [BIDS](https://bids.neuroimaging.io/) format.
This tool provides a command-line interface for easy data
conversion.

`tobids` version 1.3.0 is currently compatible with Brainvision EEG data (`.eeg`,
`.vhdr`, `.vmrk`), NIFTI fMRI data (`.nii`), and behavioral data in comma
separated values format (`.csv`).

All questions can be directed to Dave Braun: dave.braun@drexel.edu

## Installation

### Requirements

Prior to setting up ToBids, you'll need the following programs
installed:

* `pip`
* `git` - [install instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* `conda` (optional) - [install instructions](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)

You can verify whether each of these is already installed on your system by
opening a terminal and typing the name of the program followed by
`--version`, eg:

```bash
git --version
```

If the program is installed, the terminal will output the version number;
otherwise, you'll see an error.

### Installing dependencies

To configure the enviornment needed to run `tobids`, it's recommended to
use `conda` and create a fresh environment to install all needed packages
into. However, `pip` will work as well.

#### Using Conda
```bash
$ cd ~
$ git clone https://github.com/dbraun31/tobids.git
$ cd tobids
$ conda env create -f environment.yml
$ conda activate eeg
```

*Note that in order for the tool to run, you'll need to have the `eeg`
environment activated. See
[here](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment) for more about managing conda enviornments.*

#### Using Pip
```bash
$ cd ~
$ git clone https://github.com/dbraun31/tobids.git
$ cd tobids
$ pip install -r requirements.txt
```

**The following might be necessary**
If you encounter issues where `tobids` can't find required modules, try
running the line below.

```bash
$ cd ~/tobids
$ pip install .
```

### Add ToBids to path

For convenient command-line usage, a reference to `tobids` needs to be
created in a directory that's included in your `$PATH`. You can do this
with or without using admin privileges.

#### Admin privileges required

```bash
$ sudo ln -s ~/tobids/tobids.py /usr/local/bin/tobids
$ chmod +x ~/tobids/tobids.py
```

#### Admin privileges not required
```bash
$ mkdir -p ~/.local/bin
$ ln -s ~/tobids/tobids.py ~/.local/bin
$ chmod +x ~/tobids/tobids.py
$ export PATH="$HOME/.local/bin:$PATH"
```

## Usage

`tobids` has as its only required argument the path to the directory
containing the original raw data. 


To execute `tobids`, run the following command:

```bash
tobids path/to/raw/data/dir <optional/path/to/bids/dest/dir>
```

`tobids` requires that the path to the original data is specified. You can optionally supply the path to where you would like the output data to be created. If you don't supply a path for output data, `tobids` will create one in the directory in which the program was called using the name you provide for the name of the data.

After the BIDS directory is completed and populated with all necessary
files, `tobids` will run the `bids-validator` tool created by the [BIDS team](https://github.com/bids-standard/bids-validator) to ensure all files are BIDS compatible.


## Source data format

In general, it's best to include in the source data folder *only* the
minimum amount of data needed to perform the conversion. This makes things
less complicated for the tool and eases the burden of transfering data.

`tobids` makes several assumptions about the structure of the source data
that the user points to. The top-level directory that contains this data
will be referred to as the *root directory*. The root directory can have
any name.

**Assumptions:**

* **Subject inference.** Directories containing all data for each subject need to be *one level
    under* the root directory (eg, `my_source_data/subject_01`). The
    subject directories just need a number somewhere in the directory name
    to be used as the subject label; otherwise the exact naming convention
    doesn't matter. *This means no other directory should have a number in
    its name and be one level under the root directory.*
* **Session inference.** If there are sessions, session directories need to
    be *one level under* the subject directories (eg,
    `my_source_data/subject_01/session_01`).  There need to be the characters
    'sess' (case insensitive) somewhere in the directory name. 'sess' can be a
    segment of a longer word, so 'session' is fine. *This means that no other
    directory two levels under the root directory can have the characters
    'sess' **anywhere** in its name.* (which is probably not a smart
    restriction and I should improve that to also look for numbers)
* **Task inference** 
    * **EEG.** For labeling tasks for EEG data, the program will
    assume that EEG data files are stored *one level under* a directory
    labeled according to the task performed (eg,
    `my_source_data/subject_01/.../GradCPT/my_file_name.eeg`). The entire
    name of this task directory is used as the "task" argument in the BIDS
    filenames. 
    * **fMRI.** For labeling tasks for fMRI data, the program will look for
    the word immediately following the word "BOLD" in the directory name
    where all the scans are (ie, fmri root). For example,
    given the directory `12_BOLD_ExperienceSampling_run1`, the program will
    infer the task name to be `ExperienceSampling`.
    * **Behavioral**: 
        * The program assumes *all* `.csv`s in the root directory are 
            behavioral data! 
        * The program assumes that the task associated with any `.csv`
            behavioral file is the name of the directory that contains the
            `.csv`.
* **fMRI root inference.** The fMRI root is the directory containing
    subdirectories for all scans within a session. The program will search
    within a single subject's session for a directory containing
    subdirectories that contain the following keywords: `BOLD`, `AAHScout`,
    `Localizer`, and `B0map` (case sensitive). The program needs to be able
    to find at least one subdirectory for each of these keywords, and all
    subdirectories that are found need to contain at least one `.nii` file.
    The program will search for one and only one fMRI root directory. **In
    other words, make sure all scans for a single session are in one
    directory.**
* For a single subject's session, there should be exactly 1 T1w `.nii`
    file and 3 B0map `.nii` files. There are no restrictions on how many
    functional `.nii` files there can be. 




## Release notes

* **1.3.0** (2024-08-29)
    * Added BIDS compatible handling of behavioral data.
        * Behavioral data in `.csv` get put in
            `rawdata/sub-xxx/ses-xxx/func` as `*_events.tsv` along with a
            sidecar json.
        * As required, all `*_events.tsv` start with two columns `onset |
            duration`.
        * *Quirk:* Because our current experiments output all data as
            `.mat`, and some of these files can't be read by Python, one
            first has to run `helpers/process_eegfmri_behav.py` on the raw
            data directory, then run `helpers/table_to_csv.m`, then run
            `helpers/process_eegfmri_behav.py` again. Then the `tobids`
            pipeline will work as expected.

* **1.2.2** (2024-05-31)
    * Fixed an issue with EEG events writing.
        * Since we already have annotations, passing events to
            `mne_bids.write_raw_bids` was causing redundant events to be
            written.

* **1.2.1** (2024-05-24)
    * Fixed substantial bug in fMRI file naming
        * `niis` was being sorted *inside* `_get_dests()`

* **1.2.0** (2024-03-22)
    * Much more robust task and fmri root inference.
    * Fixed small issues that came up when converting only fMRI data (ie,
        no eeg)

* **1.1.2** (2024-02-21)
    * Added validation check for user to approve automatically inferred
        task name(s)
    * More intelligent session handling (particularly for when there is
        only one session).

* **1.1.1** (2023-12-18)
    * Option for more reliance on `mne_bids` for writing eeg files for more
        robust and complete BIDS conversion (default is set to using
        `mne_bids`).

* **1.1.0** (2023-11-29)
    * Support for NIFTI fMRI (`.nii`) added. Compresses to `.nii.gz`.
    * Queries the user as to whether to overwrite existing data in the BIDS
        directory.
    * Included support for multiple sessions.
    * More intelligent handling of paths.
    * More robust subject directory discovery.
    * Progress bar added.


* **1.0.0** (2023-10-14)
	* `tobids` is currently only equipped to handle BrainVision EEG data.
	* BrainVision data format (`.eeg`, `.vhdr`, `.vmrk`) is acceptable in BIDS, and so the default behavior is to simply rename and move the data files. `tobids` includes functions for converting the data to `.edf`; future iterations of `tobids` can make this feature available via a command line option.
	* `tobids` requires the source data to be structured such that the directories immediately inside the root directory are three-digit subject numbers. `tobids` will find and exclude any other directories at this level that don't match this format.

### Still to do

* Make the tool more amenable for subject-by-subject conversion.
* Make session inference look for digits.
* Figure out the coordinate system and how to produce `*_coordsystem.json`.
* How to reference the `*.bvef` file for making a montage. Might need to
    have user point to it.
