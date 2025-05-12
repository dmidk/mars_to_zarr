from pathlib import Path

import numpy as np
import xarray as xr
from loguru import logger


def write_to_zarr(ds: xr.Dataset, dataset_dict: dict) -> None:
    """Write the xarray dataset to zarr format at the specified output path.

    Args:
        ds (xr.Dataset): The xarray dataset to be written.

    Returns:
        None
    """

    data_root = dataset_dict["general"]["data_root"]
    model = dataset_dict["general"]["model"]
    level_type = dataset_dict["general"]["level_type"]

    if "zarr_fn" in dataset_dict["general"].keys():
        output_path = Path(
            f"{data_root}/{model}/zarr/{dataset_dict['general']['zarr_fn']}"
        )
    else:
        # output_path = os.path.join(data_root, "output.zarr")
        output_path = Path(f"{data_root}/{model}/zarr/output.zarr")
    # Path(output_path).mkdir(parents=True, exist_ok=True)
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info("Set coordinates correctly")

    # Do some minor mods to fix coordinates not being set correctly
    # in the gribscan output - should be done by the magician.

    ds = ds.set_index(value=("lat", "lon")).unstack("value")

    ds = ds.rename_dims({"lat": "y", "lon": "x"})

    # Assing extra coordinates, x and y
    ds.assign_coords(x=("lon", ds["lon"].values), y=("lat", ds["lat"].values))

    lat2d, lon2d = np.meshgrid(
        ds["lat"].values, ds["lon"].values, indexing="ij"
    )

    # Assign x,y coordinates to the dataset as extra coordinates
    # and set the lat/lon coordinates to the 2D arrays created above
    # This is needed for some downstream processing
    ds = ds.assign_coords(
        {
            "lat": (("y", "x"), lat2d),
            "lon": (("y", "x"), lon2d),
            "y": ds["lat"].values,
            "x": ds["lon"].values,
        }
    )

    # Rename variables to match what we had for DANRA
    logger.info("Rename variables and coordinates")
    if level_type == "surface":
        # lsm and orography are static variables,
        # select only one time step

        # Convert lsm and orography to 2D arrays (static fields)
        # if they are not already and if they are in the dataset
        if "lsm" in ds:
            static_lsm = ds["lsm"].isel(time=0).drop_vars("time")
            ds["lsm"] = static_lsm.chunk({"y": 512, "x": 512})
        if "z" in ds:
            static_orog = ds["z"].isel(time=0).drop_vars("time")
            ds["z"] = static_orog.chunk({"y": 512, "x": 512})

    elif level_type == "pressure_level":
        # Rename the 500 hPa level to 600 hPa since globalDT
        # is missing the 600 hPa data
        current_levels = ds.coords["level"].values
        new_levels = np.where(current_levels == 500, 600, current_levels)
        ds = ds.assign_coords(level=("level", new_levels))
        # Rename the "level" coordinate to "pressure"
        ds = ds.rename({"level": "pressure"})
        # Re-chunk the dataset
        ds = ds.chunk({"time": 1, "pressure": 1, "lat": 512, "lon": 512})

    rename_dict = {
            "2t": "t2m",
            "10u": "u10m",
            "10v": "v10m",
            "sp": "pres0m",
            "msl": "pres_seasurface",
            "ssr": "swavr0m",
            "str": "lwavr0m",
            "z": "orography",
            "w": "tw",
        }

    # Rename the variables in the dataset if they are in the rename_dict
    for old_name, new_name in rename_dict.items():
        if old_name in ds:
            ds = ds.rename({old_name: new_name})

    for var in ds.variables:
        ds[var].encoding.clear()

    logger.info("Write data to zarr format...")

    ds.to_zarr(str(output_path), mode="w", consolidated=False)

    logger.info(f"Dataset written to zarr format at {str(output_path)}")
