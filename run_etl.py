"""
Run whole ETL process, starting from cloning repositories as submodules,
through retrieving commits data to loading preprocessed and aggregated
data to the DB
"""

from ETL.get_repos import get_repos
from ETL.delete_repos import delete_repos
from config.repos_to_analyze import REPOS_TO_ANALYZE
from config.repos_to_analyze import SUBMODULES_DIR

if __name__ == "__main__":
    get_repos(repos_list=REPOS_TO_ANALYZE, submodules_dir=SUBMODULES_DIR)
    #delete_repos(repos_dir=SUBMODULES_DIR)
