"""
Run whole ETL process, starting from cloning repositories as submodules,
through retrieving commits data, loading preprocessed and aggregated
data to the DB to generate analysis and deploying a dashboard.
"""

import os
import subprocess
import shutil

from typing import List
from ETL.get_repos import get_repos
from ETL.delete_repos import delete_repos
from ETL.raw_data_retriever import generate_raw_data_for_all_repos
from ETL.load_data_to_db import load_data_all_repos
from config.config import *
from analysis.report_generator import ReportsGenerator

import webbrowser

def _get_repos_names() -> List[str]:
    """
    Get base names of analyzed repositories

    :return: list of repos names as strings
    """

    res = [
        os.path.basename(path)
        for path in REPOS_TO_ANALYZE
    ]

    return res


def _clean_raw_files() -> None:
    """
    Clean raw .csv files after pipeline is finished
    """
    raw_data_dirs = [path for path in os.scandir(RAW_DATA_DIR) if path.is_dir()]
    for raw_dir in raw_data_dirs:
        shutil.rmtree(raw_dir)


def _run_dashboard() -> None:
    """
    Run Dash application
    """
    subprocess.run("python app.py")



if __name__ == "__main__":
    get_repos(repos_list=REPOS_TO_ANALYZE, submodules_dir=SUBMODULES_DIR)
    generate_raw_data_for_all_repos(SUBMODULES_DIR, RAW_DATA_DIR)
    delete_repos(repos_dir=SUBMODULES_DIR)
    load_data_all_repos("raw_data")
    repos_names = _get_repos_names()
    rg = ReportsGenerator(repos_names=repos_names)
    rg.generate_reports_for_all_repos()
    if CLEAN_RAW_DATA:
        _clean_raw_files()
    if RUN_DASHBOARD:
        _run_dashboard()

