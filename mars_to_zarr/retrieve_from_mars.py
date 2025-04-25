import argparse

from loguru import logger
from ecmwfapi import ECMWFService
import yaml

def logging_wrapper(msg):
    logger.info(msg)


def retrieve_data(args: argparse.Namespace) -> list:
    """
    Retrieve data from MARS using the ECMWF API.
    Args:
        args (argparse.Namespace): Command line arguments containing the path to the yaml config file.
    Returns:
        list: A list of retrieved grib files.
    """

    # Load the yaml config file
    with open(args.config, 'r') as file:
        mars_retrieval_dict = yaml.safe_load(file)

    retrieved_grib_files = []
    for dataset_name, dataset in mars_retrieval_dict.items():
        logger.info(f"Working on dataset: {dataset_name}")
        inputs_dict = dataset["inputs"]
        outputs_dict = dataset["outputs"]

        # TODO: Uncomment the following lines to enable the retrieval process
        #server = ECMWFService("mars", log=logging_wrapper)
        #server.execute(inputs_dict, outputs_dict["fp"])

        # Save the retrieved grib files in a list
        retrieved_grib_files.append(outputs_dict["fp"])
        logger.info(f"Retrieved grib file: {outputs_dict['fp']}")

        return retrieved_grib_files
