from flask import Flask
import os

from config import config
from ETL.get_repos import get_repos
from ETL.delete_repos import delete_repos
from ETL.raw_data_retriever import generate_raw_data_for_all_repos
from ETL.load_data_to_db import load_data_all_repos

import logging.config
logging.config.fileConfig(os.path.join("config", "logging.conf"))
logger = logging.getLogger("consoleLogger")

app = Flask(__name__)


@app.route("/run_etl")
def run_etl():
    logger.info("Launching ETL process.")

    logger.info("Cloning repositories.")
    get_repos(repos_list=config.REPOS_TO_ANALYZE, submodules_dir=config.SUBMODULES_DIR)

    logger.info("Generating raw data in the format of .csv files.")
    generate_raw_data_for_all_repos(config.SUBMODULES_DIR, config.RAW_DATA_DIR)

    logger.info("Deleting submodules.")
    delete_repos(repos_dir=config.SUBMODULES_DIR)

    logger.info("Uploading data to Postgres DB.")
    load_data_all_repos(config.RAW_DATA_DIR)

    return "ETL process finished"

if __name__ == "__main__":
    app.run(host="0.0.0.0")
