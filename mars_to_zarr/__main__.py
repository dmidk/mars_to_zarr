import sys
import os
from argparse import ArgumentParser

from loguru import logger

from mars_to_zarr.retrieve_from_mars import retrieve_data
from mars_to_zarr.read_source import read_source


def _setup_argparse():
    """Set up argument parser."""

    parser = ArgumentParser(
        description="Retrieve grib from MARS and convert to zarr"
    )
    parser.add_argument(
        "--config",
        help="Path to the yaml config file to load.",
        default="example.globalDT.yaml"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase output verbosity",
    )

    return parser


def run():

    argparser = _setup_argparse()
    args = argparser.parse_args()

    # Retrieve grib from MARS
    retrieve_data(args)
    logger.info("Have already retrieved the data!")

    # Read the retrieved grib data
    read_source(args)


if __name__ == "__main__":
    logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")

    # Check that $HOME/.ecmwfapirc exists
    if not os.path.exists(os.path.expanduser("~/.ecmwfapirc")):
        url="https://api.ecmwf.int/v1/key/"
        logger.error(f"Please create a ~/.ecmwfapirc file with your ECMWF API key\n \
                      get your key from {url}")

        sys.exit(1)

    run()