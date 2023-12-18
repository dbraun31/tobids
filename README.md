# ToBids

ToBids is a general Python tool developed for the [Dynamic Brain and Mind Lab](https://sites.google.com/site/aaronkucyi)
to convert raw neuro data to [BIDS](https://bids.neuroimaging.io/) format.
This tool provides a command-line interface for easy data
conversion.

`tobids` version 1.1.0 is currently compatible with Brainvision EEG data (`.eeg`,
`.vhdr`, `.vmrk`) and NIFTI fMRI data (`.nii`).

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

`tobids` makes several assumptions about the structure of the source data
that the user points to. The top-level directory that contains this data
will be referred to as the *root directory*. The root directory can have
any name.

**Assumptions:**

* Directories containing all data for each subject need to be *one level
    under* the root directory (eg, `my_source_data/subject_01`). The
    subject directories just need a number somewhere in the directory name
    to be used as the subject label; otherwise the exact naming convention
    doesn't matter.
* If there are sessions, session directories need to be *one level under*
    the subject directories (eg, `my_source_data/subject_01/session_01`).
    Again, there just needs to be a number somewhere in the name of this
    session directory. If there are no sessions, you can omit session
    folders.
* EEG data files are stored *one level under* a directory labeled according
    to the task performed (eg,
    `my_source_data/subject_01/.../GradCPT/my_file_name.eeg`). The entire
    name of this task directory is used as the "task" argument in the
    BIDS filenames.
* Raw fMRI data are assumed to have extension `.nii` and need to be located
    *two levels below* the main fMRI directory containing the different
    scans.



## Release notes

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

* More sophisticated command-line argument parsing.
* Figure out the coordinate system and how to produce `*_coordsystem.json`.
* How to reference the `*.bvef` file for making a montage. Might need to
    have user point to it.
