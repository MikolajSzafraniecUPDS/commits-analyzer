"""
Run whole ETL process, starting from cloning repositories as submodules,
through retrieving commits data to loading preprocessed and aggregated
data to the DB
"""

import os

from typing import List
from ETL.get_repos import get_repos
from ETL.delete_repos import delete_repos
from ETL.raw_data_retriever import generate_raw_data_for_all_repos
from ETL.load_data_to_db import load_data_all_repos
from config.config import REPOS_TO_ANALYZE, SUBMODULES_DIR, RAW_DATA_DIR
from analysis.report_generator import ReportsGenerator

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

if __name__ == "__main__":
    get_repos(repos_list=REPOS_TO_ANALYZE, submodules_dir=SUBMODULES_DIR)
    generate_raw_data_for_all_repos(SUBMODULES_DIR, RAW_DATA_DIR)
    delete_repos(repos_dir=SUBMODULES_DIR)
    load_data_all_repos("raw_data")
    repos_names = _get_repos_names()
    rg = ReportsGenerator(repos_names=repos_names)
    rg.generate_reports_for_all_repos()
