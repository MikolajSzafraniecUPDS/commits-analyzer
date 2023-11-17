"""
Tools responsible for conducting preprocessing of the data - it transforms
raw .csv files to pandas table ready to load to the database.
"""

import os
import re
import numpy as np

import pandas as pd
import logging.config

from datetime import datetime
from typing import Dict, List, Tuple
from config.raw_files_config import OUTPUT_FILES
from nltk.stem import PorterStemmer

# Format in which date will be stored in the Postgres database
_DATE_FORMAT = "%Y-%m-%d"

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


class AuthorsSummaryTableProvider:

    """
    Class responsible for generating table containing summary
    of commits authors activity. This table will be useful both
    for analysis and dashboard.
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
        Load tables containing general info and number of insertions / deletions

        :return: dictionary containing tables stored as pandas DataFrames
        """
        res = {
            file_type: pd.read_csv(
                os.path.join(self.raw_data_path, file_name),
                sep=";", header=0
            )
            for file_type, file_name in OUTPUT_FILES.items()
            if file_type in ["commits_info", "insertions_deletions"]
        }

        return res

    def get_authors_summary_table(self) -> pd.DataFrame:
        """
        Get results - table containing summary of authors activity. It
        contains following columns:
            - autor_name
            - autor_email
            - number_of_commits
            - number_of_insertions
            - number_of_deletions
            - min_date - first day when author contributed
            - max_date - last day when author contributed
            - days_of_activity - difference between max date and min date
            - insertions_deletions_ratio - ratio of insertions sum to deletions sum

        :return: summary table as pandas DataFrame
        """

        repo_name = os.path.basename(self.raw_data_path)
        logger.info("Preparing commits authors stats tab for repo '{0}'".format(repo_name))

        input_data = self._load_required_data()
        df_insertions_deletions_joined = input_data.get(
            "commits_info"
        ).merge(
            input_data.get("insertions_deletions"),
            how="left", on="commit_hash"
        )

        ### Add column containing date
        df_insertions_deletions_joined["commit_date"] = \
            df_insertions_deletions_joined.commit_unix_time.apply(
                lambda x: datetime.fromtimestamp(x)
            )

        summary = df_insertions_deletions_joined.groupby(
            ["author_email", "author_name"]
        ).agg(
            number_of_insertions=("insertions", "sum"),
            number_of_deletions=("deletions", "sum"),
            number_of_commits=("commit_hash", "count"),
            min_date=("commit_date", "min"),
            max_date=("commit_date", "max")
        ).reset_index()

        res = summary.assign(
            insertions_deletions_ratio=summary.number_of_insertions / summary.number_of_deletions
        )

        # Calculated number of days between first and last contribution,
        # transform dates to string
        res["days_of_activity"] = res.max_date - res.min_date
        res["days_of_activity"] = res["days_of_activity"].dt.days  # Retrieve days from timedelta object
        res["min_date"] = res.min_date.apply(lambda x: x.strftime(_DATE_FORMAT))
        res["max_date"] = res.max_date.apply(lambda x: x.strftime(_DATE_FORMAT))

        # In cases when number of deletions is queal to zero we will
        # replace Inf with max value + 1 (to indicate that the ratio
        # for given author is the highest).
        max_ratio = res.loc[res['insertions_deletions_ratio'] != np.inf, 'insertions_deletions_ratio'].max() + 1
        res['insertions_deletions_ratio'].replace(np.inf, max_ratio, inplace=True)

        return res


class CommitMessagesStatsProvider:

    """
    Class responsible for providing tables containing information
    about words statistics in commit messages.
    """

    def __init__(self, raw_data_path: str):
        """
        Create an instance of the class

        :param raw_data_path: path to directory where raw data
            are stored in the .csv format
        """
        self.raw_data_path = raw_data_path

    def _load_required_data(self) -> pd.DataFrame:
        """
        Load table containing commit messages.

        :return: commit messages table as pandas DataFrame
        """
        file_path = os.path.join(
            self.raw_data_path, OUTPUT_FILES.get("commits_messages")
        )
        res = pd.read_csv(
            file_path, sep=";", header=0
        )

        return res

    @staticmethod
    def _preprocess_words(words: List[str]) -> List[str]:
        """
        Take a list of words from commit message, transform each word
        to lowercase, get rid of signs which are not characters
        (numbers, series of special characters, etc.) and words shorter than
        4 letters ('a', 'an', 'and', 'for', etc.)

        :param words: list of words (effect of sentence.split(" ") operation)
        :return: list containing preprocessed and filtered words
        """

        words_lowercase = [w.lower() for w in words]
        # Get rid of all special characters and numbers
        special_chars_numbers_excluded = [
            re.sub('[^a-z]', '', w)
            for w in words_lowercase
        ]

        short_words_excluded = list(
            filter(
                lambda x: len(x) > 3,
                special_chars_numbers_excluded
            )
        )

        return short_words_excluded

    @staticmethod
    def _stem_words(words: List[str]) -> List[str]:
        """
        In order to improve word frequency analysis we will create additional
        column with words stems. For example, simple grouping will treat 'strings'
        and 'string' as different words. However, they have the same meaning, the only
        difference is the fact that one of them is in singular and another in
        plural form. Stemming procedure will remove plural suffix in such a case, then
        both words will have the same, singular form.

        Procedure below will use PorterStemmer. Stemming is not perfect, in most cases
        we would achieve better results with Lemmatization (using for example WordNetLemmatizer
        from NLTK package), however it requires to download language corpora and is more
        time-consuming. We decided that to achieve goal of this analysis stemming will be
        sufficient.

        :param words: list of words to stem
        :return: list of stemmed words
        """
        ps = PorterStemmer()
        res = [ps.stem(w) for w in words]
        return res

    def get_output_tables(self) -> Dict[str, pd.DataFrame]:
        """
        Get output tables containing words frequency analysis. Three tables will be
        returned of structure as follows:

        Table containing all words from commit messages and their stemmed versions
        a) all_words_tab:
            - raw_word - column containing raw words
            - stemmed_word - column containing columns after stemming

        Frequency stats for raw words
        b) raw_words_count:
            - raw_word
            - raw_word_freq - frequency of given raw word

        Frequency stats for stemmed words
        c) stemmed_words_count:
            - stemmed_word
            - stemmed_word_freq - frequency of given stemmed version

        :return: dictionary containing output table with following keys:
            - all_words_tab
            - raw_words_count
            - stemmed_words_count
        """

        repo_name = os.path.basename(self.raw_data_path)
        logger.info("Preparing messages stats tables for repo '{0}'".format(repo_name))

        messages_tab = self._load_required_data()

        # Split messages into single words
        words_lists = messages_tab.commit_message.map(
            lambda x: str(x).split(" ")
        )

        words_preprocessed = words_lists.apply(
            lambda x: self._preprocess_words(x)
        )
        words_stemmed = words_preprocessed.apply(
            lambda x: self._stem_words(x)
        )

        all_words_tab = pd.DataFrame(
            {
                "raw_word": words_preprocessed,
                "stemmed_word": words_stemmed
            }
        ).explode(
            ["raw_word", "stemmed_word"]  # Explode words list to tabular form
        ).dropna()  # After preprocessing some of the messages might have produced empty lists
                    # if they contained only numbers and special characters

        raw_words_count = all_words_tab.groupby("raw_word").agg(
            raw_word_freq=("raw_word", "count")
        ).reset_index()

        stemmed_words_count = all_words_tab.groupby("stemmed_word").agg(
            stemmed_word_freq=("stemmed_word", "count")
        ).reset_index()

        res = {
            "all_words_tab": all_words_tab,
            "raw_words_count": raw_words_count,
            "stemmed_words_count": stemmed_words_count
        }

        return res
