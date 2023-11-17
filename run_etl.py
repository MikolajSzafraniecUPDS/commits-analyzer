"""
Run whole ETL process, starting from cloning repositories as submodules,
through retrieving commits data to loading preprocessed and aggregated
data to the DB
"""

from ETL.get_repos import get_repos
from ETL.delete_repos import delete_repos
from ETL.raw_data_retriever import generate_raw_data_for_all_repos
from ETL.data_preprocessing import GeneralTableProvider
from config.repos_to_analyze import REPOS_TO_ANALYZE
from config.paths import SUBMODULES_DIR, RAW_DATA_DIR


if __name__ == "__main__":
    #get_repos(repos_list=REPOS_TO_ANALYZE, submodules_dir=SUBMODULES_DIR)
    #generate_raw_data_for_all_repos(SUBMODULES_DIR, RAW_DATA_DIR)
    #delete_repos(repos_dir=SUBMODULES_DIR)
    print(
        GeneralTableProvider("raw_data/boto3").get_general_info_table()
    )
