import xarray as xr
from loguru import logger
from pathlib import Path

def write_to_zarr(ds: xr.Dataset) -> None:
    """Write the xarray dataset to zarr format at the specified output path.

    Args:
        ds (xr.Dataset): The xarray dataset to be written.

    Returns:
        None
    """

    output_path = "output.zarr"
    Path(output_path).mkdir(parents=True, exist_ok=True)

    # Do some minor mods to fix coordinates not being set correctly
    # in the gribscan output - should be done by the magician.
    ds = ds.set_index(value=("lat", "lon"))
    ds = ds.set_index(value=("lat", "lon")).unstack("value")

    ds.to_zarr(output_path, mode='w', consolidated=True)

    logger.info(f"Dataset written to zarr format at {output_path}")
