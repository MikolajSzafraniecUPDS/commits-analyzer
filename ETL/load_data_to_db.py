"""
Get and transform raw data from .csv files and load tables
to the postgres database
"""

import os

import logging.config

import pandas as pd
from database.get_db_engine import get_db_engine
from sqlalchemy import Engine
from config.config import *
from ETL.data_preprocessing import GeneralTableProvider, AuthorsSummaryTableProvider, CommitMessagesStatsProvider

logging.config.fileConfig(os.path.join("config", "logging.conf"))
logger = logging.getLogger("consoleLogger")


def load_single_table_to_db(
        tab_to_load: pd.DataFrame,
        table_prefix: str,
        table_type: str,
        db_engine: Engine
) -> int:
    """
    Load singe table to the databae

    :param tab_to_load: table to load to db as pandas DataFrame
    :param table_prefix: table prefix (repo name)
    :param table_type: type of the table
    :param db_engine: db engine created by 'create_engine' method

    :return: SQL code
    """

    table_name = DB_TABLES_NAMES.get(table_type).format(table_prefix)
    res = tab_to_load.to_sql(
        table_name, db_engine, if_exists="replace"
    )

    return res


def load_data_single_repo(raw_data_path: str, db_engine: Engine, repo_name: str = None) -> None:
    """
    Load all tables for single repository. Please note that tables names
    are in format {repo_name}_table_suffix. As default the directory name
    is treat as repo name - to change this behaviour please set 'repo_name'
    argument.

    If given table already exists in the database it will be replaced.

    :param raw_data_path: path to directory where raw data is stored
    :param db_engine: db engine created by 'create_engine' method
    :param repo_name: repo name which will be set as tables prefix. Name
        of raw files directory if None
    """

    if repo_name is None:
        repo_name = os.path.basename(raw_data_path)

    general_info_tab = GeneralTableProvider(raw_data_path).get_general_info_table()
    authors_stats_tab = AuthorsSummaryTableProvider(raw_data_path).get_authors_summary_table()
    commits_messages_stats_tabs = CommitMessagesStatsProvider(raw_data_path).get_output_tables()

    logger.info("Loading general info table to db, repo: '{0}'".format(repo_name))
    load_single_table_to_db(general_info_tab, repo_name, "general_info", db_engine)

    logger.info("Loading author stats table to db, repo: '{0}'".format(repo_name))
    load_single_table_to_db(authors_stats_tab, repo_name, "authors_stats", db_engine)

    logger.info("Loading messages_all_words table to db, repo: '{0}'".format(repo_name))
    load_single_table_to_db(
        commits_messages_stats_tabs.get("all_words_tab"),
        repo_name,
        "messages_all_words",
        db_engine
    )

    logger.info("Loading messages_raw_words_freq table to db, repo: '{0}'".format(repo_name))
    load_single_table_to_db(
        commits_messages_stats_tabs.get("raw_words_count"),
        repo_name,
        "messages_raw_words_freq",
        db_engine
    )

    logger.info("Loading messages_stemmed_words_freq table to db, repo: '{0}'".format(repo_name))
    load_single_table_to_db(
        commits_messages_stats_tabs.get("stemmed_words_count"),
        repo_name,
        "messages_stemmed_words_freq",
        db_engine
    )


def load_data_all_repos(raw_data_dir: str) -> None:
    """
    Load data for all analyzed repositories to the db

    :param raw_data_dir: directory where raw data is stored
    """

    engine = get_db_engine(inside_compose_network=True)

    # Get paths to all repos in given dir
    raw_data_paths = [
        f.path
        for f in os.scandir(raw_data_dir) if f.is_dir()
    ]

    logger.info("Found following directories with data: {0}".format(raw_data_paths))

    for single_path in raw_data_paths:
        load_data_single_repo(
            single_path, db_engine=engine
        )
