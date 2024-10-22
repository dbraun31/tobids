# Changelog

* **1.4.0** (2024-10-22)
    - `tobids` is celebrating its first birthday! 🎉

    - Full support and more robust task inference for rt-fMRI behavioral data.
        - Onset times are time-locked to start of scan.
    - This comes with an updated set of assumptions (see README).
    - More robust session inference. Session dirs now need the characters `ses` *and* a digit somewhere in the dir name.

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


