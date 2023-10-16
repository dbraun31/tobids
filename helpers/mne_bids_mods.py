# Taken from mne_bids.dig
import warnings
from mne.io.constants import FIFF
from mne_bids.config import MNE_STR_TO_FRAME
from mne_bids.config import MNE_FRAME_TO_STR
from mne_bids.config import MNE_TO_BIDS_FRAMES
from mne_bids.config import BIDS_COORD_FRAME_DESCRIPTIONS
from mne_bids.path import BIDSPath
from mne_bids.utils import warn

def _write_dig_bids(bids_path, raw, montage=None, acpc_aligned=False, overwrite=False):
    """Write BIDS formatted DigMontage from Raw instance.

    Handles coordsystem.json and electrodes.tsv writing
    from DigMontage.

    Parameters
    ----------
    bids_path : BIDSPath
        Path in the BIDS dataset to save the ``electrodes.tsv``
        and ``coordsystem.json`` file for. ``datatype``
        attribute must be ``eeg``, or ``ieeg``. For ``meg``
        data, ``electrodes.tsv`` are not saved.
    raw : mne.io.Raw
        The data as MNE-Python Raw object.
    montage : mne.channels.DigMontage | None
        The montage to use rather than the one in ``raw`` if it
        must be transformed from the "head" coordinate frame.
    acpc_aligned : bool
        Whether "mri" space is aligned to ACPC.
    overwrite : bool
        Whether to overwrite the existing file.
        Defaults to False.

    """
    # write electrodes data for iEEG and EEG
    unit = "m"  # defaults to meters

    if montage is None:
        montage = raw.get_montage()
    else:  # assign montage to raw but supress any coordinate transforms
        montage = montage.copy()  # don't modify original
        montage_coord_frame = montage.get_positions()["coord_frame"]
        fids = [
            d
            for d in montage.dig  # save to add back
            if d["kind"] == FIFF.FIFFV_POINT_CARDINAL
        ]
        montage.remove_fiducials()  # prevent coordinate transform
        with warnings.catch_warnings():
            warnings.filterwarnings(
                action="ignore",
                category=RuntimeWarning,
                message=".*nasion not found",
                module="mne",
            )
            raw.set_montage(montage)
        for ch in raw.info["chs"]:
            ch["coord_frame"] = MNE_STR_TO_FRAME[montage_coord_frame]
        for d in raw.info["dig"]:
            d["coord_frame"] = MNE_STR_TO_FRAME[montage_coord_frame]
        with raw.info._unlock():  # add back fiducials
            raw.info["dig"] = fids + raw.info["dig"]

    # get the accepted mne-python coordinate frames
    coord_frame_int = int(montage.dig[0]["coord_frame"])
    mne_coord_frame = MNE_FRAME_TO_STR.get(coord_frame_int, None)
    coord_frame = MNE_TO_BIDS_FRAMES.get(mne_coord_frame, None)

    if coord_frame == "CapTrak" and bids_path.datatype in ("eeg", "nirs"):
        pos = raw.get_montage().get_positions()
        if any([pos[fid_key] is None for fid_key in ("nasion", "lpa", "rpa")]):
            raise RuntimeError(
                "'head' coordinate frame must contain nasion "
                "and left and right pre-auricular point "
                "landmarks"
            )

    if (
        bids_path.datatype == "ieeg"
        and bids_path.space in (None, "ACPC")
        and mne_coord_frame == "ras"
    ):
        if not acpc_aligned:
            raise RuntimeError(
                "`acpc_aligned` is False, if your T1 is not aligned "
                "to ACPC and the coordinates are in fact in ACPC "
                "space there will be no way to relate the coordinates "
                "to the T1. If the T1 is ACPC-aligned, use "
                "`acpc_aligned=True`"
            )
        coord_frame = "ACPC"

    if bids_path.space is None:  # no space, use MNE coord frame
        if coord_frame is None:  # if no MNE coord frame, skip
            warn(
                "Coordinate frame could not be inferred from the raw object "
                "and the BIDSPath.space was none, skipping the writing of "
                "channel positions"
            )
            return
    else:  # either a space and an MNE coord frame or just a space
        if coord_frame is None:  # just a space, use that
            coord_frame = bids_path.space
        else:  # space and raw have coordinate frame, check match
            if bids_path.space != coord_frame and not (
                coord_frame == "fsaverage" and bids_path.space == "MNI305"
            ):  # fsaverage == MNI305
                raise ValueError(
                    "Coordinates in the raw object or montage "
                    f"are in the {coord_frame} coordinate "
                    "frame but BIDSPath.space is "
                    f"{bids_path.space}"
                )

    # create electrodes/coordsystem files using a subset of entities
    # that are specified for these files in the specification
    coord_file_entities = {
        "root": bids_path.root,
        "datatype": bids_path.datatype,
        "subject": bids_path.subject,
        "session": bids_path.session,
        "acquisition": bids_path.acquisition,
        "space": None if bids_path.datatype == "nirs" else coord_frame,
    }
    channels_suffix = "optodes" if bids_path.datatype == "nirs" else "electrodes"
    _channels_fun = (
        _write_optodes_tsv if bids_path.datatype == "nirs" else _write_electrodes_tsv
    )
    channels_path = BIDSPath(
        **coord_file_entities, suffix=channels_suffix, extension=".tsv"
    )
    coordsystem_path = BIDSPath(
        **coord_file_entities, suffix="coordsystem", extension=".json"
    )

    # Now write the data to the elec coords and the coordsystem

    # (Dave) dropping the below line bc I have my own function for this
    #_channels_fun(raw, channels_path, bids_path.datatype, overwrite)

    coordsystem = _write_coordsystem_json(
        raw=raw,
        unit=unit,
        hpi_coord_system="n/a",
        sensor_coord_system=coord_frame,
        fname=coordsystem_path,
        datatype=bids_path.datatype,
        overwrite=overwrite,
    )

    return coordsystem


def _write_coordsystem_json(
    *,
    raw,
    unit,
    hpi_coord_system,
    sensor_coord_system,
    fname,
    datatype,
    overwrite=False,
):
    """Create a coordsystem.json file and save it.
    ** I'm (dave) modifying it to just return the json instead of writing
    it directly

    Parameters
    ----------
    raw : mne.io.Raw
        The data as MNE-Python Raw object.
    unit : str
        Units to be used in the coordsystem specification,
        as in BIDS_COORDINATE_UNITS.
    hpi_coord_system : str
        Name of the coordinate system for the head coils.
    sensor_coord_system : str | tuple of str
        Name of the coordinate system for the sensor positions.
        If a tuple of strings, should be in the form:
        ``(BIDS coordinate frame, MNE coordinate frame)``.
    fname : str
        Filename to save the coordsystem.json to.
    datatype : str
        Type of the data recording. Can be ``meg``, ``eeg``,
        or ``ieeg``.
    overwrite : bool
        Whether to overwrite the existing file.
        Defaults to False.

    """
    if raw.get_montage() is None:
        dig = list()
        coords = dict()
    else:
        montage = raw.get_montage()
        pos = montage.get_positions()
        dig = list() if montage.dig is None else montage.dig
        coords = dict(
            NAS=list() if pos["nasion"] is None else pos["nasion"].tolist(),
            LPA=list() if pos["lpa"] is None else pos["lpa"].tolist(),
            RPA=list() if pos["rpa"] is None else pos["rpa"].tolist(),
        )

    # get the coordinate frame description
    sensor_coord_system_descr = BIDS_COORD_FRAME_DESCRIPTIONS.get(
        sensor_coord_system.lower(), "n/a"
    )

    # create the coordinate json data structure based on 'datatype'
    if datatype == "meg":
        hpi = {d["ident"]: d for d in dig if d["kind"] == FIFF.FIFFV_POINT_HPI}
        if hpi:
            for ident in hpi.keys():
                coords["coil%d" % ident] = hpi[ident]["r"].tolist()

        fid_json = {
            "MEGCoordinateSystem": sensor_coord_system,
            "MEGCoordinateUnits": unit,  # XXX validate this
            "MEGCoordinateSystemDescription": sensor_coord_system_descr,
            "HeadCoilCoordinates": coords,
            "HeadCoilCoordinateSystem": hpi_coord_system,
            "HeadCoilCoordinateUnits": unit,  # XXX validate this
            "AnatomicalLandmarkCoordinates": coords,
            "AnatomicalLandmarkCoordinateSystem": sensor_coord_system,
            "AnatomicalLandmarkCoordinateUnits": unit,
        }
    elif datatype == "eeg":
        fid_json = {
            "EEGCoordinateSystem": sensor_coord_system,
            "EEGCoordinateUnits": unit,
            "EEGCoordinateSystemDescription": sensor_coord_system_descr,
            "AnatomicalLandmarkCoordinates": coords,
            "AnatomicalLandmarkCoordinateSystem": sensor_coord_system,
            "AnatomicalLandmarkCoordinateUnits": unit,
        }
    elif datatype == "ieeg":
        fid_json = {
            # (Other, Pixels, ACPC)
            "iEEGCoordinateSystem": sensor_coord_system,
            "iEEGCoordinateSystemDescription": sensor_coord_system_descr,
            "iEEGCoordinateUnits": unit,  # m (MNE), mm, cm , or pixels
        }
    elif datatype == "nirs":
        fid_json = {
            "NIRSCoordinateSystem": sensor_coord_system,
            "NIRSCoordinateSystemDescription": sensor_coord_system_descr,
            "NIRSCoordinateUnits": unit,
        }

    # note that any coordsystem.json file shared within sessions
    # will be the same across all runs (currently). So
    # overwrite is set to True always
    # XXX: improve later when BIDS is updated
    # check that there already exists a coordsystem.json
    if Path(fname).exists() and not overwrite:
        with open(fname, "r", encoding="utf-8-sig") as fin:
            coordsystem_dict = json.load(fin)
        if fid_json != coordsystem_dict:
            raise RuntimeError(
                f"Trying to write coordsystem.json, but it already "
                f"exists at {fname} and the contents do not match. "
                f"You must differentiate this coordsystem.json file "
                f'from the existing one, or set "overwrite" to True.'
            )
    return fid_json


