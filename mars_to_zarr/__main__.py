import os
import shutil
import sys
from argparse import ArgumentParser
from pathlib import Path

import yaml
from loguru import logger

from mars_to_zarr.read_source import read_source
from mars_to_zarr.retrieve_from_mars import retrieve_data
from mars_to_zarr.write_to_zarr import write_to_zarr


def _setup_argparse():
    """Set up argument parser."""

    parser = ArgumentParser(
        description="Retrieve grib from MARS and convert to zarr"
    )
    parser.add_argument(
        "--config",
        help="Path to the yaml config file to load.",
        default="example.globalDT.yaml",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase output verbosity",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the cache before running",
        default=False,
    )

    return parser


def run():

    argparser = _setup_argparse()
    args = argparser.parse_args()

    # Load the yaml config file
    with open(args.config, "r") as f:
        mars_to_zarr_dict = yaml.safe_load(f)

    for dataset_name, dataset_dict in mars_to_zarr_dict.items():
        logger.info(f"Working on dataset: {dataset_name}")

        # clear the cache if requested
        if args.clear_cache:
            logger.info("Clearing cache")

            model_root = Path(dataset_dict["general"]["data_root"]) / Path(
                dataset_dict["general"]["model"]
            )

            caches = [
                model_root / "grib",
                model_root / "zarr",
                model_root / "zarr",
            ]
            for cache in caches:
                if cache.exists():
                    logger.info(f"Deleting {cache}")
                    shutil.rmtree(cache)

        # Retrieve grib from MARS
        retrieve_data(dataset_dict)

        # Read the retrieved grib data
        ds = read_source(dataset_dict)

        # Write the xarray dataset to zarr format
        write_to_zarr(ds, dataset_dict)


if __name__ == "__main__":
    logger.add(
        sys.stderr,
        format="{time} {level} {message}",
        filter="my_module",
        level="INFO",
    )

    # Check that $HOME/.ecmwfapirc exists
    if not os.path.exists(os.path.expanduser("~/.ecmwfapirc")):
        url = "https://api.ecmwf.int/v1/key/"
        logger.error(
            f"Please create a ~/.ecmwfapirc file with your ECMWF API key\n \
                      get your key from {url}"
        )

        sys.exit(1)

    run()
