import argparse

from loguru import logger
from ecmwfapi import ECMWFService

EUROPEAN_AREA = "74/-27/33/45"

def logging_wrapper(msg):
    logger.info(msg)


def retrieve_data(args: argparse.Namespace):

    server = ECMWFService("mars", log=logging_wrapper)

    area = EUROPEAN_AREA

    server.execute(
    {
        "class": "od",
        "stream": "oper",
        "date" : "2025-03-08",
        "time": "12:00:00",
        "expver": "1",
        "Area": area,
        "Grid": "0.25/0.25",
        "type": "fc",
        "levtype": "sfc",
        "param": "151/165/166/167/172",
        "step": "0/6/12/18/24",
    },
    "ifs.grib")
