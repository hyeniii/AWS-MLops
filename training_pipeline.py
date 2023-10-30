import os
import argparse
import datetime
from pathlib import Path
import yaml
import logging.config

import src.get_data as gd

logging.config.fileConfig("config/logging/local.conf")
logger = logging.getLogger("rentals")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Acquire, clean, and create features from clouds data"
    )
    parser.add_argument(
        "--config", default="config/default-config.yaml", help="Path to configuration file"
    )
    args = parser.parse_args()

    # Load configuration file for parameters and run config
    with open(args.config, "r") as f:
        try:
            config = yaml.load(f, Loader=yaml.FullLoader)
        except yaml.error.YAMLError as e:
            logger.error("Error while loading configuration from %s", args.config)
            raise yaml.error.YAMLError from e
        else:
            logger.info("Configuration file loaded from %s", args.config)

    run_config = config.get("run_config", {})

    # Set up output directory for saving artifacts
    now = int(datetime.datetime.now().timestamp())
    print(now)
    artifacts = Path(run_config.get("output", "runs")) / str(now)
    artifacts.mkdir(parents=True)

    # Save config file to artifacts directory for traceability
    # with (artifacts / "config.yaml").open("w") as f:
    #     yaml.dump(config, f)

    # Acquire data from online repository and save to disk
    dataPath = Path("data") / str(now)
    gd.download_data(run_config["data_source"], dataPath)
    download_files = [file for file in os.listdir(dataPath) if file.endswith(".7z")]
    print(download_files)
    gd.unzip_file(dataPath / download_files[0], dataPath)

