import gribscan
import xarray as xr
import os
import json
from pathlib import Path

# Get $HOME for the user for the gribscan index directory

hdir = os.path.expanduser("~")

if not os.path.exists(os.path.join(hdir, ".gribscan")):
    os.makedirs(os.path.join(hdir, ".gribscan"))
    os.path.join(hdir, ".gribscan")
else:
    os.path.join(hdir, ".gribscan")

grib_index_directory = os.environ.get(
    "GRIBSCAN_INDEX_DIR", os.path.join(hdir, ".gribscan")
)

FP_GRIB_INDECIES_DEFAULT = Path(grib_index_directory)

def read_grib_to_xarray(grib_files: list) -> xr.Dataset:
    """
    Read a GRIB file and convert it to an xarray Dataset.

    Args:
        grib_files (list): List of paths to the GRIB files.

    Returns:
        xarray.Dataset: The converted xarray Dataset.
    """

    # Initialize the Magician object
    magician = gribscan.Magician()

    fp_forecast_root = Path(grib_files[0]).parent

    # Build indices
    indexfiles = []
    for gribfile in grib_files:
        indexfile = FP_GRIB_INDECIES_DEFAULT / (Path(gribfile).name + ".idx")
        print(gribfile)
        if not indexfile.exists():
            print(f"Creating index for {gribfile} in {FP_GRIB_INDECIES_DEFAULT}")
            gribscan.write_index(gribfile=str(gribfile), idxfile=indexfile)
        else:
            print(f"Index already exists for {gribfile} in {FP_GRIB_INDECIES_DEFAULT}")

        indexfiles.append(indexfile)

    refs = gribscan.grib_magic(
        indexfiles,
        magician=magician,
        global_prefix=str(fp_forecast_root) + "/",
    )

    fn = f"{fp_forecast_root.name}.zarr.json"
    fp_zarr_json = fp_forecast_root / fn
    with open(fp_zarr_json, "w") as f:
        json.dump(refs, f)
    print(f"Built zarr index for analysis time {fp_forecast_root.name} in {fp_zarr_json}")

    ds = xr.open_zarr(f"reference::{fp_zarr_json}", consolidated=False)
