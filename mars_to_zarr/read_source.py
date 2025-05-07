import json
from pathlib import Path
from sys import platform

import eccodes
import gribscan
import xarray as xr
from loguru import logger

# set the eccodes definitions path, older versions of eccodes require this
if eccodes.__version__ < "2.20.0" and platform == "linux":
    gribscan.eccodes.codes_set_definitions_path(
        "/usr/share/eccodes/definitions"
    )
elif eccodes.__version__ < "2.20.0" and platform == "darwin":
    gribscan.eccodes.codes_set_definitions_path(
        "/opt/homebrew/share/eccodes/definitions"
    )


def read_source(dataset_dict: dict) -> xr.Dataset:
    """
    Read the grib files and convert them to zarr format.

    Args:
        mars_to_zarr_dict (dict):
            Dictionary containing the dataset information.

    Returns:
        xr.Dataset: The dataset in zarr format.
    """

    # Format the grib file path
    grib_fp = Path(
        dataset_dict["general"]["data_root"],
        dataset_dict["general"]["model"],
        "grib",
        dataset_dict["general"]["grib_fn"],
    )

    data_root = dataset_dict["general"]["data_root"]
    model = dataset_dict["general"]["model"]
    level_type = dataset_dict["general"]["level_type"]

    fp_index = Path(
        f"{data_root}/{model}/refs/mars_to_zarr.jsons/{level_type}.json"
    )

    if not fp_index.exists():
        fp_index.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Index grib file {grib_fp}")
        # cast to string to ensure pathlib.Path isn't passed in as
        # gribscan.write_index assumes the path is a string
        gribscan.write_index(gribfile=str(grib_fp), idxfile=fp_index)
        logger.info(f"Created indices: {fp_index}")

    # Use the IFS Magician
    magician = gribscan.magician.IFSMagician()

    logger.info(f"Build references for {fp_index}")
    ref = gribscan.grib_magic(
        filenames=[str(fp_index)],
        magician=magician,
        global_prefix="",
    )

    logger.info(f"Created references for {fp_index}")

    logger.info("Build zarr index")
    fn = f"{level_type}.zarr.json"
    fp_zarr_json = fp_index.parent / fn
    with open(fp_zarr_json, "w") as f:
        json.dump(ref, f)

    logger.info("Built zarr index")

    with open(fp_zarr_json) as f:
        original = json.load(f)

    if level_type == "surface":
        zarr_group = "atm2d"
    elif level_type == "pressure_level":
        zarr_group = "atm3d"

    assert zarr_group in original, "Expected top-level 'atm2d' key!"

    # Need to flatten the structure to match the zarr format
    # The top-level group should be the zarr group name
    # and the "refs" key should contain the original references
    # for the group
    flattened_ref = {"version": 1, "refs": original[zarr_group]}

    # Ensure .zgroup exists
    flattened_ref["refs"].setdefault(".zgroup", json.dumps({"zarr_format": 2}))

    # Overwrite the file
    with open(fp_zarr_json, "w") as f:
        json.dump(flattened_ref, f)

    ds = xr.open_zarr(f"reference::{fp_zarr_json}", consolidated=False)

    return ds
