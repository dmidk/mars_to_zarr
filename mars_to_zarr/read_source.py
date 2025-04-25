import datetime
from pathlib import Path

import gribscan
import isodate
from loguru import logger
import yaml
import xarray as xr

# set the eccodes definitions path, older versions of eccodes require this
gribscan.eccodes.codes_set_definitions_path("/usr/share/eccodes/definitions")


def read_source(args):
    """."""
    # Load the yaml config file
    with open(args.config, 'r') as file:
        mars_retrieval_dict = yaml.safe_load(file)

    for dataset_name, dataset in mars_retrieval_dict.items():
        logger.info(f"Working on dataset: {dataset_name}")

        grib_fp = dataset["outputs"]["fp"]
        inputs = dataset["inputs"]
        t_analysis = inputs["date"] + inputs["time"]
        level_type = "surface"

        fp_index = Path(f"/dmidata/users/ea/mars/globalDT/refs/{t_analysis}.jsons/{level_type}.json")

        if not fp_index.exists():
            fp_index.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Index grib file {grib_fp}")
            # cast to string to ensure pathlib.Path isn't passed in as
            # gribscan.write_index assumes the path is a string
            gribscan.write_index(gribfile=grib_fp, idxfile=fp_index)
            logger.info(f"Created indices: {fp_index}")

        # Use the IFS Magician
        magician = gribscan.magician.IFSMagician()

        logger.info(f"Build references for {fp_index}")
        ref = gribscan.grib_magic(
            filenames=[str(fp_index)],
            magician=magician,
            global_prefix="",
        )

        logger.info(f"Created references: {ref}")