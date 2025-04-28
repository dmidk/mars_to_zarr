from pathlib import Path

from ecmwfapi import ECMWFService
from loguru import logger


def logging_wrapper(msg):
    logger.info(msg)


def retrieve_data(mars_to_zarr_dict: dict):
    """Retrieve data from the ECMWF MARS catalogue"""

    for dataset_name, dataset_dict in mars_to_zarr_dict.items():
        logger.info(f"Working on dataset: {dataset_name}")

        # Format the grib file path
        grib_fp = Path(
            dataset_dict["general"]["data_root"],
            dataset_dict["general"]["model"],
            "grib",
            dataset_dict["general"]["grib_fn"],
        )

        # Create the directory if it doesn't exist
        grib_fp.parent.mkdir(parents=True, exist_ok=True)

        # Get the mars request dict for the specified dataset
        mars_request_dict = dataset_dict["mars_request"]

        # Perform the mars retrieval
        server = ECMWFService("mars", log=logging_wrapper)
        server.execute(mars_request_dict, grib_fp)
