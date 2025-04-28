import datetime
from pathlib import Path
import json

import gribscan
import isodate
from loguru import logger
import xarray as xr

# set the eccodes definitions path, older versions of eccodes require this
gribscan.eccodes.codes_set_definitions_path("/usr/share/eccodes/definitions")


def read_source(mars_to_zarr_dict):
    """."""

    for dataset_name, dataset_dict in mars_to_zarr_dict.items():
        logger.info(f"Working on dataset: {dataset_name}")

        # Format the grib file path
        grib_fp = Path(
            dataset_dict["general"]["data_root"],
            dataset_dict["general"]["model"],
            "grib",
            dataset_dict["general"]["grib_fn"]
        )
        date = dataset_dict["mars_request"]["date"]
        time = dataset_dict["mars_request"]["time"]
        t_analysis = date + "Z" + time
        data_root = dataset_dict["general"]["data_root"]
        model = dataset_dict["general"]["model"]
        level_type = dataset_dict["general"]["level_type"]

        #fp_index = Path(f"{data_root}/{model}/refs/{t_analysis}.jsons/{level_type}.json")
        fp_index = Path(f"{data_root}/{model}/refs/mars_to_zarr.jsons/{level_type}.json")

        if not fp_index.exists():
            fp_index.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Index grib file {grib_fp}")
            # cast to string to ensure pathlib.Path isn't passed in as
            # gribscan.write_index assumes the path is a string
            gribscan.write_index(gribfile=str(grib_fp), idxfile=fp_index)
            logger.info(f"Created indices: {fp_index}")

        # Use the IFS Magician
        magician = gribscan.magician.IFSMagician()

        logger.info(f"Build references for {fp_index}")
        ref = gribscan.grib_magic(
            filenames=[str(fp_index)],
            magician=magician,
            global_prefix="",
        )

        logger.info(f"Created references for {fp_index}")

        logger.info("Build zarr index")
        fn = f"{level_type}.zarr.json"
        fp_zarr_json = fp_index.parent / fn
        with open(fp_zarr_json, "w") as f:
            json.dump(ref, f)
        print(fp_zarr_json)

        logger.info(
            f"Built zarr index"
        )

        with open(fp_zarr_json) as f:
            original = json.load(f)
        
        if level_type == "surface":
            zarr_group = "atm2d"
        elif level_type == "pressure_level":
            zarr_group = "atm3d"

        # Confirm zarr_group is there
        print(original.keys())  # should be ['atm2d']
        assert zarr_group in original, "Expected top-level 'atm2d' key!"
        
        # Flatten
        flattened_ref = {
            "version": 1,
            "refs": original[zarr_group]
        }
        
        # Ensure .zgroup exists
        flattened_ref["refs"].setdefault(".zgroup", json.dumps({"zarr_format": 2}))
        
        # Overwrite the file
        with open(fp_zarr_json, "w") as f:
            json.dump(flattened_ref, f)

        #import sys
        #with open(fp_zarr_json) as f:
        #    ref_loaded = json.load(f)
        
        #print("ref_loaded.keys()")
        #print(ref_loaded.keys())  # should include: 'refs', 'version', optionally 'templates'

        #print("ref_loaded['atm2d'].keys()")
        #print(ref_loaded["atm2d"].keys())  # should include: 'refs', 'version', optionally 'templates'
        ##print('ref_loaded["atm2d"]') 
        ##print(ref_loaded["atm2d"])
        
        ## Check top-level group
        ##print(".zgroup" in ref_loaded["refs"])  # should be True
        #print(".zgroup" in ref_loaded["atm2d"]["refs"])  # should be True
        #sys.exit()

        #ds = xr.open_zarr(f"reference::/dmidata/projects/nwp/grib-indecies/dmidata/cache/mdcprd/gdb/grib2/dini/sf/2025042200/analysis_time_20250422T000000+0000__suite_name_DINI__data_kind_sf__level_type_heightAboveGround__forecast_duration_6:00:00.zarr.json", consolidated=False)
        #print(ds)
        #ds = xr.open_zarr(f"reference::/dmidata/projects/nwp/grib-indecies/dmidata/cache/mdcprd/gdb/grib2/dini/sf/2025042200/analysis_time_20250422T000000+0000__suite_name_DINI__data_kind_sf__level_type_heightAboveGround__forecast_duration_6:00:00.zarr.json", consolidated=False, group="atm2d")
        #print(ds)

        ds = xr.open_zarr(f"reference::{fp_zarr_json}", consolidated=False)
        ##ds = xr.open_dataset(f"reference::{fp_zarr_json}", consolidated=False, engine="zarr")
        print(ds)
