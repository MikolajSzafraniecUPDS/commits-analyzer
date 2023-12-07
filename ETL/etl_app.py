import requests
import os
import importlib

from flask import Flask
from config import config
from ETL.get_repos import get_repos, GetReposError
from ETL.cleanup import delete_repos, cleanup, ReposDeletingError
from ETL.raw_data_retriever import generate_raw_data_for_all_repos, RawDataGenerationError
from ETL.load_data_to_db import load_data_all_repos, DBLoadingError

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

    # Reload config in case it was updated after deploying docker container
    importlib.reload(config)

    logger.info("Launching ETL process.")
    try:
        logger.info("Cloning repositories.")
        get_repos(repos_list=config.REPOS_TO_ANALYZE, submodules_dir=config.SUBMODULES_DIR)

        logger.info("Generating raw data in the format of .csv files.")
        generate_raw_data_for_all_repos(config.SUBMODULES_DIR, config.RAW_DATA_DIR)

        logger.info("Deleting submodules.")
        delete_repos(repos_dir=config.SUBMODULES_DIR)

        logger.info("Uploading data to Postgres DB.")
        load_data_all_repos(config.RAW_DATA_DIR)
    except GetReposError as gre:
        error_msg = str(gre)
        res = app.response_class(
            response="ETL process failed at the stage of cloning submodules. Error msg:\n'{0}'".format(
                error_msg
            ),
            status=500
        )
    except RawDataGenerationError as rge:
        error_msg = str(rge)
        res = app.response_class(
            response="ETL process failed at the stage of generating raw data. Error msg:\n'{0}'".format(
                error_msg
            ),
            status=500
        )
    except ReposDeletingError as rde:
        error_msg = str(rde)
        res = app.response_class(
            response="ETL process failed at the stage of deleting submodules. Error msg:\n'{0}'".format(
                error_msg
            ),
            status=500
        )
    except DBLoadingError as dle:
        error_msg = str(dle)
        res = app.response_class(
            response="ETL process failed at the stage of uploading data to DB. Error msg:\n'{0}'".format(
                error_msg
            ),
            status=500
        )
    else:
        res = app.response_class(
            response="ETL process finished successfully",
            status=200
        )

    if res.status_code == 500 or config.CLEAN_RAW_DATA:
        try:
            logger.info("Running cleanup")
            cleanup(config.SUBMODULES_DIR, config.RAW_DATA_DIR)
        except Exception as e:
            logger.info("Cleanup failed: {0}".format(str(e)))
        else:
            logger.info("Cleanup succesfull")

    return res


if __name__ == "__main__":
    app.run(host="0.0.0.0")
