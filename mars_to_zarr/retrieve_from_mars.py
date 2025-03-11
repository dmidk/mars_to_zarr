import argparse

from loguru import logger
from ecmwfapi import ECMWFDataServer


def logging_wrapper(msg):
    logger.info(msg)


def retrieve_data(args: argparse.Namespace):
    server = ECMWFDataServer(log=logging_wrapper)

    server.retrieve({
        "class": "ti",
        "dataset": "tigge",
        "date": "2025-03-01/to/2025-03-09",
        "expver": "prod",
        "grid": "0.5/0.5",
        "levtype": "sfc",
        "origin": "ecmf",
        "param": "167",
        "step": "0",
        "time": "00:00:00",
        "type": "cf",
        "target": "output"
    })
