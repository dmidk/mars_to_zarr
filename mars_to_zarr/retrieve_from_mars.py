from pathlib import Path

from ecmwfapi import ECMWFService
from loguru import logger


def logging_wrapper(msg):
    logger.info(msg)


def retrieve_data(mars_to_zarr_dict: dict):
    """Retrieve data from the ECMWF MARS catalogue"""

    # Format the grib file path
    grib_fp = Path(
        mars_to_zarr_dict["general"]["data_root"],
        mars_to_zarr_dict["general"]["model"],
        "grib",
        mars_to_zarr_dict["general"]["grib_fn"],
    )

    # Create the directory if it doesn't exist
    grib_fp.parent.mkdir(parents=True, exist_ok=True)

    # Get the mars request dict for the specified dataset
    mars_request_dict = mars_to_zarr_dict["mars_request"]

    # Perform the mars retrieval
    server = ECMWFService("mars", log=logging_wrapper)
    server.execute(mars_request_dict, grib_fp)
