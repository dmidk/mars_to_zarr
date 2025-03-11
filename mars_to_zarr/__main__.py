import sys
import os
from argparse import ArgumentParser
#3rd party
from loguru import logger

#internal
from mars_to_zarr.retrieve_from_mars import retrieve_data

def run():


    parser = ArgumentParser(
        description="Train or evaluate NeurWP models for LAM"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase output verbosity",
    )

    args = parser.parse_args()

    retrieve_data(args)


if __name__ == "__main__":
    logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")

    # Check that $HOME/.ecmwfapirc exists
    if not os.path.exists(os.path.expanduser("~/.ecmwfapirc")):
        url="https://api.ecmwf.int/v1/key/"
        logger.error(f"Please create a ~/.ecmwfapirc file with your ECMWF API key\n \
                      get your key from {url}")

        sys.exit(1)

    run()