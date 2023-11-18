"""
Run whole ETL process, starting from cloning repositories as submodules,
through retrieving commits data to loading preprocessed and aggregated
data to the DB
"""

from ETL.get_repos import get_repos
from ETL.delete_repos import delete_repos
from ETL.raw_data_retriever import generate_raw_data_for_all_repos
from ETL.load_data_to_db import load_data_all_repos
from config.repos_to_analyze import REPOS_TO_ANALYZE
from config.paths import SUBMODULES_DIR, RAW_DATA_DIR
from analysis.plots_and_tables_generator import PlotsAndTablesGenerator
from sqlalchemy import create_engine
from config.db_credentials import *
from analysis.report_generator import ReportsGenerator

if __name__ == "__main__":
    #get_repos(repos_list=REPOS_TO_ANALYZE, submodules_dir=SUBMODULES_DIR)
    #generate_raw_data_for_all_repos(SUBMODULES_DIR, RAW_DATA_DIR)
    #delete_repos(repos_dir=SUBMODULES_DIR)
    #load_data_all_repos("raw_data")
    # conn_string = "postgresql://{username}:{password}@{host}:{port}/{db_name}".format(
    #     username=POSTGRES_USER,
    #     password=POSTGRES_PASSWORD,
    #     host=POSTGRES_HOST,
    #     port=POSTGRES_PORT,
    #     db_name=POSTGRES_DB
    # )
    # engine = create_engine(conn_string)
    # ptg = PlotsAndTablesGenerator("boto3", db_engine=engine)
    # ptg.generate_all_plots_and_tables_for_given_report()
    # ptg.generate_commits_time_of_day_table_and_plot()
    # ptg.generate_commits_day_of_week_plot()
    # ptg.generate_contributors_activity_tables()
    # ptg.generate_word_clouds_imgs_and_tables()
    # ptg.generate_time_to_merge_info()
    # ptg.get_insertions_deletions_stats()
    rg = ReportsGenerator()
    rg.generate_reports_for_all_repos()
