# ToBids

ToBids is a general Python tool developed for the [Dynamic Mind and Brain Lab](https://sites.google.com/site/aaronkucyi)
to convert raw neuro data to [BIDS](https://bids.neuroimaging.io/) format.
This tool provides a command-line interface for easy data
conversion.

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
containing the original raw data. `tobids` currently has the **important
limitation** that the directory pointed to with the original raw data needs
to be structured thus:

```
├── sample_data
│   ├── 006
│   ├── 007
│   └── 008
```

where `sample_data` is the original directory, and each next-level directory is a subject number containing all of a subject's data.

To execute `tobids`, run the following command:

```bash
tobids path/to/raw/data/dir <optional/path/to/bids/dest/dir>
```

`tobids` requires that the path to the original data is specified. You can optionally supply the path to where you would like the output data to be created. If you don't supply a path for output data, `tobids` will create one in the directory in which the program was called using the name you provide for the name of the data.

After the BIDS directory is completed and populated with all necessary
files, `tobids` will run the `bids-validator` tool created by the [BIDS team](https://github.com/bids-standard/bids-validator) to ensure all files are BIDS compatible.


## Release notes

* **1.0.0**
	* `tobids` is currently only equipped to handle BrainVision EEG data.
	* BrainVision data format (`.eeg`, `.vhdr`, `.vmrk`) is acceptable in BIDS, and so the default behavior is to simply rename and move the data files. `tobids` includes functions for converting the data to `.edf`; future iterations of `tobids` can make this feature available via a command line option.
	* As noted above, `tobids` requires the source data to be structured such that the directories immediately inside the root directory are three-digit subject numbers. `tobids` will find and exclude any other directories at this level that don't match this format.

### Still to do

* Improve function documentation.
* More sophisticated command-line argument parsing.
* Generalize to other data types.
* Figure out the coordinate system and how to produce `*_coordsystem.json`.
* How to reference the `*.bvef` file for making a montage. Might need to
    have user point to it.
* Probably lots of other things...
