# ToBids

ToBids is a general Python tool developed for the [Dynamic Brain and Mind Lab](https://sites.google.com/site/aaronkucyi)
to convert raw neuro data to [BIDS](https://bids.neuroimaging.io/) format.
This tool provides a command-line interface for easy data
conversion.

`tobids` version 1.3.1 is currently compatible with Brainvision EEG data (`.eeg`,
`.vhdr`, `.vmrk`) and NIFTI fMRI data (`.nii`). Functionality for
behavioral data is very specific to the needs of the Dynamic Brain and Mind
Lab and will likely break for more general behavioral data. A future
release will add an option to disregard behavioral data and only convert
brain data.

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
    `my_source_data/subject_01/session_01`).  There need to be the
    characters 'ses' (case insensitive) somewhere in the directory name and
    also at least one digit somwhere in the directory name. 'sess' can be a
    segment of a longer word, so 'session' is fine. *This means that no
    non-session directory two levels under the root directory can have the
    characters `ses` and a digit **anywhere** in its directory name.*
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
        * All files matching the pattern `*_city_mnt_*.mat` are GradCPT
            data.
        * All files named `ptbP.mat` are experience sampling data.
            * These files should have the subject and run number somewhere
                in the path matching the pattern: `[Ss]ub[-_]\d+`, and same
                for run.
            * These files should have a corresponding file in the same
                directory matching the pattern: `*_P.mat` storing
                additional timing information.
        * *All* other `.csv`s in the root directory are assumed to be
            experience sampling data. This is a strong assumption!

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

See the [CHANGELOG.md](CHANGELOG.md) for detailed release notes.

### Still to do

* Make the tool more amenable for subject-by-subject conversion.
* Make session inference look for digits.
* Make more use of `pathlib.BIDSPath` in the writers.
* Add option to disregard behavioral data.
