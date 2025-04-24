import argparse

from loguru import logger
from ecmwfapi import ECMWFService
import yaml

def logging_wrapper(msg):
    logger.info(msg)


def retrieve_data(args: argparse.Namespace):

    # Load the yaml config file
    with open(args.config, 'r') as file:
        mars_retrieval_dict = yaml.safe_load(file)
    
    for dataset_name, dataset in mars_retrieval_dict.items():
        logger.info(f"Working on dataset: {dataset_name}")
        inputs_dict = dataset["inputs"]
        outputs_dict = dataset["outputs"]

        server = ECMWFService("mars", log=logging_wrapper)
        server.execute(inputs_dict, outputs_dict["fp"])
