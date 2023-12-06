import requests
from flask import Flask
import os

from config import config
from ETL.get_repos import get_repos
from ETL.cleanup import delete_repos, cleanup
from ETL.raw_data_retriever import generate_raw_data_for_all_repos
from ETL.load_data_to_db import load_data_all_repos

import logging.config
logging.config.fileConfig(os.path.join("config", "logging.conf"))
logger = logging.getLogger("consoleLogger")

app = Flask(__name__)


@app.route("/run_etl")
def run_etl() -> requests.Response:
    """
    Run ETL process when the /run_etl endpoint is triggered.

    :return: HTTP response
    """

    logger.info("Launching ETL process.")
    try:
        logger.info("Cloning repositories.")
        get_repos(repos_list=config.REPOS_TO_ANALYZE, submodules_dir=config.SUBMODULES_DIR)
    except Exception as e:
        error_msg = str(e)
        res = app.response_class(
            response="ETL process failed at the stage of cloning submodules. Error msg:\n'{0}'".format(
                error_msg
            ),
            status=500
        )

        return res

    try:
        logger.info("Generating raw data in the format of .csv files.")
        generate_raw_data_for_all_repos(config.SUBMODULES_DIR, config.RAW_DATA_DIR)
    except Exception as e:
        error_msg = str(e)
        res = app.response_class(
            response="ETL process failed at the stage of generating raw data. Error msg:\n'{0}'".format(
                error_msg
            ),
            status=500
        )

        return res

    try:
        logger.info("Deleting submodules.")
        delete_repos(repos_dir=config.SUBMODULES_DIR)
    except Exception as e:
        error_msg = str(e)
        res = app.response_class(
            response="ETL process failed at the stage of deleting submodules. Error msg:\n'{0}'".format(
                error_msg
            ),
            status=500
        )

        return res

    try:
        logger.info("Uploading data to Postgres DB.")
        load_data_all_repos(config.RAW_DATA_DIR)
    except Exception as e:
        error_msg = str(e)
        res = app.response_class(
            response="ETL process failed at the stage of uploading data to DB. Error msg:\n'{0}'".format(
                error_msg
            ),
            status=500
        )

        return res
    else:
        res = app.response_class(
            response="ETL process finished successfully",
            status=200
        )

    if res.status_code == 500:
        try:
            logger.info("Running cleanup")
            cleanup(config.SUBMODULES_DIR, config.RAW_DATA_DIR)
        except Exception as e:
            logger.info("Cleanup failed: {0}".format(str(e)))

    return res


if __name__ == "__main__":
    app.run(host="0.0.0.0")
