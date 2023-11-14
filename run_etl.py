"""
Run whole ETL process, starting from cloning repositories as submodules,
through retrieving commits data to loading preprocessed and aggregated
data to the DB
"""

from ETL.get_repos import get_repos
from config.repos_to_analyze import REPOS_TO_ANALYZE

if __name__ == "__main__":
    get_repos(REPOS_TO_ANALYZE)