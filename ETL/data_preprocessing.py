"""
Tools responsible for conducting preprocessing of the data - it transforms
raw .csv files to pandas table ready to load to the database.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict
import logging.config

from config.raw_files_config import OUTPUT_FILES

# Format in which date will be stored in the Postgres database
_DATE_FORMAT = "%Y-%m-d"

logging.config.fileConfig(os.path.join("config", "logging.conf"))
logger = logging.getLogger("consoleLogger")


class GeneralTableProvider:
    """
    Class responsible for generating 'general table', storing all
    basic information about commits. Output pandas table consists of
    following fields:

    - commit_hash
    - author_email
    - author_name
    - commit_timestamp
    - commiter_email
    - commiter_name
    - date_str - date in the provided format ('%Y-%d-%m' recommended)
    - commit_year
    - commit_month
    - commit_month_day
    - commit_week_day
    - commit_hour
    - commit_message
    - insertions_number
    - deletions_number
    - time_before_merge - time to nearest merge
    - nearest_merge_hash - hash of nearest merge
    """

    def __init__(self, raw_data_path: str):
        """
        Create an instance of the class

        :param raw_data_path: path to directory where raw data
            are stored in the .csv format
        """
        self.raw_data_path = raw_data_path

    def _load_required_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all raw dataset from provided directory, using OUTPUT_FILES
        specification from config.

        :return: dictionary containing tables stored as pandas DataFrames
        """
        res = {
            file_type: pd.read_csv(
                os.path.join(self.raw_data_path, file_name),
                sep=";", header=0
            )
            for file_type, file_name in OUTPUT_FILES.items()
        }

        return res

    @staticmethod
    def _get_date_details(df_row: pd.Series) -> Dict[str, object]:
        """
        Retrieve all date details from unix timestamp, including:
            - date in provided format (%Y-%m-%d recommended)
            - year
            - month
            - day
            - day of week
            - hour

        It will be returned as dictionary, which will allow to
        use this function inside the 'apply' method and directly
        merge this information to the source DataFrame as additional
        columns

        :param df_row: row of the general info DataFrame
        :return: dictionary containing date's details
        """
        dt_object = datetime.fromtimestamp(df_row["commit_unix_time"])
        res = {
            "date_str": dt_object.strftime(_DATE_FORMAT),
            "commit_year": dt_object.year,
            "commit_month": dt_object.month,
            "commit_month_day": dt_object.day,
            "commit_week_day": dt_object.isoweekday(),
            "commit_hour": dt_object.hour
        }

        return res

    def _append_date_details(self, general_info_tab: pd.DataFrame) -> pd.DataFrame:
        """
        Append date details to the general info table

        :param general_info_tab: general info table
        :return: input DataFrame with date details appended
        """

        dates_details = general_info_tab.apply(
            lambda x: self._get_date_details(x),
            axis='columns', result_type='expand'
        )

        res = pd.concat([general_info_tab, dates_details], axis='columns')
        return res

    @staticmethod
    def _append_merges_info(
            general_info_tab: pd.DataFrame,
            merge_info_tab: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Append info about nearest future merge (hash of the merge and timestamp)
        to the general info table.

        :param general_info_tab: table containing general info
        :param merge_info_tab: table containing merge info
        :return: general info tab with nearest merge details joined
        """

        merge_info_duplicates_rm = merge_info_tab.drop_duplicates(
            "merge_unix_time"
        ).set_index("merge_unix_time", drop=False).sort_index()

        commits_timestamps_unique = general_info_tab.commit_unix_time.unique()
        # To each commit timestamp find closest merge timestamp higher than it
        merges_info_filled = merge_info_duplicates_rm.reindex(commits_timestamps_unique, method="bfill")
        merges_info_filled.index.names = ["commit_unix_time"]
        merges_info_filled = merges_info_filled.reset_index()
        res = general_info_tab.merge(merges_info_filled, how="left", on="commit_unix_time")
        return res

    def get_general_info_table(self) -> pd.DataFrame:
        """
        Provide DataFrame with general info about commits. The process contains a few
        steps, including reading raw data from .csv files, merging and simple preprocessing.

        :return: DataFrame containing results
        """

        repo_name = os.path.basename(self.raw_data_path)
        logger.info("Preparing general info tab for repo '{0}'".format(repo_name))

        logger.info("Reading raw data from .csv files")
        raw_data_all_tables = self._load_required_data()

        logger.info("Appending date details")
        general_tab_dates_append = self._append_date_details(
            raw_data_all_tables.get("commits_info")
        )

        logger.info("Joining messages")
        general_tab_messages_append = general_tab_dates_append.merge(
            raw_data_all_tables.get("commits_messages"),
            how="left", on="commit_hash"
        )

        logger.info("Joining insertions and deletions info")
        general_tab_insertions_deletions_append = general_tab_messages_append.merge(
            raw_data_all_tables.get("insertions_deletions"),
            how="left", on="commit_hash"
        )

        logger.info("Appending merge info")
        res = self._append_merges_info(
            general_tab_insertions_deletions_append,
            raw_data_all_tables.get("merges_info")
        )

        return res
