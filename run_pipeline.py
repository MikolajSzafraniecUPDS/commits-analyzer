"""
Run whole ETL process, starting from cloning repositories as submodules,
through retrieving commits data, loading preprocessed and aggregated
data to the DB to generate analysis and deploying a dashboard.
"""

import os
import subprocess
import shutil
import requests

from typing import List
from config import config
from analysis.report_generator import ReportsGenerator
import logging.config

logging.config.fileConfig(os.path.join("config", "logging.conf"))
logger = logging.getLogger("consoleLogger")

def _get_repos_names() -> List[str]:
    """
    Get base names of analyzed repositories

    :return: list of repos names as strings
    """

    res = [
        os.path.basename(path)
        for path in config.REPOS_TO_ANALYZE
    ]

    return res


def _clean_raw_files() -> None:
    """
    Clean raw .csv files after pipeline is finished
    """
    raw_data_dirs = [path for path in os.scandir(config.RAW_DATA_DIR) if path.is_dir()]
    for raw_dir in raw_data_dirs:
        shutil.rmtree(raw_dir)


def _run_dashboard() -> None:
    """
    Run Dash application
    """
    subprocess.run("python app.py", shell=True)


def _config_to_str():
    """
    Convert configuration to string in order to pass it to logger.
    """

    output_str = ""
    for single_setting in dir(config):
        if not single_setting.startswith("__"):
            setting_val = "{0}: {1}".format(
                single_setting,
                getattr(config, single_setting)
            ) + "\n"
            output_str += setting_val

    return output_str


def _run_etl():
    r = requests.get("http://127.0.0.1:5000/run_etl", timeout=1000)
    return r


if __name__ == "__main__":

    logger.info("Launching commits-analyzer pipeline.")

    config_str = _config_to_str()
    logger.info("\nConfiguration:\n{0}".format(config_str))

    etl_reponse = _run_etl()
    logger.info("ETL process finished, response code: {0}, response message: {1}".format(
        etl_reponse.status_code, etl_reponse.content.decode())
    )

    if not etl_reponse.ok:
        raise requests.RequestException(
            "ETL process failed, error code: {0}, message: {1}".format(
                etl_reponse.status_code, etl_reponse.content.decode()
            )
        )

    # logger.info("Generating .md and .pdf reports.")
    # repos_names = _get_repos_names()
    # rg = ReportsGenerator(repos_names=repos_names)
    # rg.generate_reports_for_all_repos()
    #
    # logger.info("Reports generated")
    #
    # if config.CLEAN_RAW_DATA:
    #     logger.info("Deleting raw files.")
    #     _clean_raw_files()
    #
    # if config.RUN_DASHBOARD:
    #     logger.info("Hosting dashboard at localhost, port: {0}".format(config.DASH_PORT))
    #     _run_dashboard()
