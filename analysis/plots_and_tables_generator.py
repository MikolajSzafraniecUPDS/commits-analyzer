"""
Tools responsible for generating plots and tables for
the purpose of analysis
"""

import os
import pandas as pd
import seaborn as sns
import numpy as np
import logging.config

from config.config import *
from typing import Dict
from sqlalchemy import Engine
from typing import List
from wordcloud import WordCloud
from datetime import datetime

import matplotlib.pyplot as plt

logging.config.fileConfig(os.path.join("config", "logging.conf"))
logger = logging.getLogger("consoleLogger")

class PlotsAndTablesGenerator:

    """
    Class responsible for generating plots and tables for particular
    repository
    """

    def __init__(self, repo_name: str, db_engine: Engine):
        """
        Initialize the instance of the class

        :param repo_name: prefix of DB table, usually a name of the
            repository
        :param db_engine: database Engine object
        """

        self.repo_name = repo_name
        self.output_path = os.path.join(ANALYSIS_RESULTS_DIR, repo_name, "assets")
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        self.all_tabs = self._get_required_tables(repo_name, db_engine)

    @staticmethod
    def _get_required_tables(table_prefix: str, db_engine: Engine) -> Dict[str, pd.DataFrame]:
        """
        Get all tables required for the analysis

        :param table_prefix: prefix of the table, usually name of the repository
        :param db_engine: database Engine object
        :return: dictionary containing all required tables as pandas DataFrames
        """

        res = {
            key: pd.read_sql_table(
                table_name.format(table_prefix), db_engine
            )
            for key, table_name in DB_TABLES_NAMES.items()
        }

        return res

    @staticmethod
    def _render_pandas_table(
            data: pd.DataFrame, col_width: float= 3.0, row_height: float = 0.625,
            font_size: int = 14, header_color: str ='#40466e',
            row_colors: List[str] = ['#f1f1f2', 'w'], edge_color='w',
                         bbox=[0, 0, 1, 1], header_columns=0,
                         ax=None, **kwargs):

        """
        Render pandas table as a .png image.

        :param data: input table
        :param col_width: width of column
        :param row_height: height of a row
        :param font_size: font size
        :param header_color: color of headers
        :param row_colors: color of rows
        :param edge_color: colors of edge
        :param bbox: a bounding box to draw the table into
        :param header_columns: number of row storing headers
        :param ax: pyplot axis
        :param kwargs: additional params which will bepassed
            to the ax.table method
        :return:
        """

        if ax is None:
            size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
            fig, ax = plt.subplots(figsize=size)
            ax.axis('off')
        mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)
        mpl_table.auto_set_font_size(False)
        mpl_table.set_fontsize(font_size)

        for k, cell in mpl_table._cells.items():
            cell.set_edgecolor(edge_color)
            if k[0] == 0 or k[1] < header_columns:
                cell.set_text_props(weight='bold', color='w')
                cell.set_facecolor(header_color)
            else:
                cell.set_facecolor(row_colors[k[0] % len(row_colors)])
        return ax.get_figure(), ax

    def generate_commits_time_of_day_table_and_plot(self) -> None:

        """
        Create table and plot of sum of commits per time of a day
        and save them to files.
        """

        output_path_tab = os.path.join(
            self.output_path, "commits_time_of_day_table.png"
        )
        output_path_img = os.path.join(
            self.output_path, "commits_time_of_day_plot.png"
        )

        commits_time_of_day_table = self.all_tabs.get(
            "general_info"
        ).groupby("commit_hour").agg(
            number_of_commits=("commit_hour", "count")
        ).reset_index().sort_values(
            "commit_hour", ascending=True
        )

        fig, ax = self._render_pandas_table(commits_time_of_day_table, header_columns=0, col_width=4.0)
        fig.savefig(output_path_tab)

        fig, ax = plt.subplots()
        sns.barplot(commits_time_of_day_table, x="commit_hour", y="number_of_commits", ax=ax)
        plt.savefig(output_path_img)

    def generate_commits_day_of_week_plot(self) -> None:
        """
        Create boxplot presenting the distribution of number of
        commits per weekday.
        """

        output_path_img = os.path.join(
            self.output_path, "commits_day_of_week_plot.png"
        )

        commits_day_of_week_table = self.all_tabs.get(
            "general_info"
        ).groupby(["date_str", "commit_week_day"]).agg(
            number_of_commits=("commit_hash", "count")
        ).reset_index().sort_values(
            "commit_week_day", ascending=True
        )

        fig, ax = plt.subplots()
        sns.catplot(
            data=commits_day_of_week_table,
            x="commit_week_day",
            y="number_of_commits",
            ax=ax,
            kind="box"
        )
        plt.savefig(output_path_img)

    def generate_contributors_activity_tables(self):
        """
        Generate tables showing activity and productivity of contributors:
            - Top
        """

        output_path_commits_tab = os.path.join(
            self.output_path, "top_contributors_number_of_commits.png"
        )
        output_path_insertions_tab = os.path.join(
            self.output_path, "top_contributors_number_of_insertions.png"
        )
        output_path_insertions_deletions_ratio_tab = os.path.join(
            self.output_path, "insertions_deletions_ratio.png"
        )
        output_path_number_of_commits_per_day = os.path.join(
            self.output_path, "commits_number_per_day.png"
        )
        output_path_number_of_insertions_per_day = os.path.join(
            self.output_path, "insertions_number_per_day.png"
        )

        author_tab_stats = self.all_tabs.get("authors_stats")

        top_contributors_number_of_commits = author_tab_stats[
            ["author_name", "number_of_commits"]
        ].sort_values(
            "number_of_commits", ascending=False
        ).head(TOP_N_CONTRIBUTORS)

        top_contributors_number_of_insertions = author_tab_stats[
            ["author_name", "number_of_insertions"]
        ].sort_values(
            "number_of_insertions", ascending=False
        ).head(TOP_N_CONTRIBUTORS)

        # We want to exclude contributors which are not much active from this
        # summary
        authors_tab_filteres = author_tab_stats[
            (author_tab_stats.number_of_insertions > MIN_INSERTIONS) &
            (author_tab_stats.number_of_deletions > MIN_DELETIONS)
        ]
        top_contributors_insertions_deletions_ratio = authors_tab_filteres[
            ["author_name", "insertions_deletions_ratio"]
        ].sort_values(
            "insertions_deletions_ratio", ascending=False
        ).round(1).head(TOP_N_CONTRIBUTORS)

        top_contributors_commits_per_day = author_tab_stats[
            ["author_name"]
        ].assign(
            commits_per_day=author_tab_stats.number_of_commits /
                            author_tab_stats.days_of_activity
        ).sort_values(
            "commits_per_day", ascending=False
        ).round(1).head(TOP_N_CONTRIBUTORS)

        top_contributors_insertions_per_day = author_tab_stats[
            ["author_name"]
        ].assign(
            insertions_per_day=author_tab_stats.number_of_insertions /
                               author_tab_stats.days_of_activity
        ).sort_values(
            "insertions_per_day", ascending=False
        ).round(1).head(TOP_N_CONTRIBUTORS)

        fig, ax = self._render_pandas_table(top_contributors_number_of_commits, header_columns=0, col_width=4.0)
        fig.savefig(output_path_commits_tab)

        fig, ax = self._render_pandas_table(top_contributors_number_of_insertions, header_columns=0, col_width=4.0)
        fig.savefig(output_path_insertions_tab)

        fig, ax = self._render_pandas_table(top_contributors_insertions_deletions_ratio, header_columns=0, col_width=4.0)
        fig.savefig(output_path_insertions_deletions_ratio_tab)

        fig, ax = self._render_pandas_table(top_contributors_commits_per_day, header_columns=0, col_width=4.0)
        fig.savefig(output_path_number_of_commits_per_day)

        fig, ax = self._render_pandas_table(top_contributors_insertions_per_day, header_columns=0, col_width=4.0)
        fig.savefig(output_path_number_of_insertions_per_day)

    @staticmethod
    def _render_word_cloud_image(freq_table: pd.DataFrame, output_file: str) -> None:
        """
        Generate word cloud image. *freq_table* needs to be pandas
        DataFrame with first column containing words and second column
        containing frequencies.

        :param freq_table: frequency table of words
        :param output_file: path to the file where image will be saved
        """
        frequencies_dict = {
            word: freq
            for word, freq in freq_table.values
        }

        wordcloud = WordCloud(
            width=600,
            height=400,
            max_words=100,
            relative_scaling="auto",
            normalize_plurals=False
        )
        wordcloud.generate_from_frequencies(frequencies=frequencies_dict)
        wordcloud.to_file(output_file)

    def generate_word_clouds_imgs_and_tables(self):
        """
        Generate tables showing words frequency and word cloud
        images both for raw and stemmed words.
        """

        raw_words_freq_tab = self.all_tabs.get(
            "messages_raw_words_freq"
        ).drop(columns="index")
        stemmed_words_freq_tab = self.all_tabs.get(
            "messages_stemmed_words_freq"
        ).drop(columns="index")

        output_path_top_raw_words = os.path.join(
            self.output_path, "top_raw_words_table.png"
        )
        output_path_raw_word_cloud = os.path.join(
            self.output_path, "word_cloud_raw_words.png"
        )
        output_path_top_stemmed_words = os.path.join(
            self.output_path, "top_stemmed_words_table.png"
        )
        output_path_stemmed_word_cloud = os.path.join(
            self.output_path, "word_cloud_stemmed_words.png"
        )

        raw_words_freq_tab_filtered = raw_words_freq_tab.sort_values(
            "raw_word_freq", ascending=False
        ).head(TOP_N_WORDS)

        stemmed_words_freq_tab_filtered = stemmed_words_freq_tab.sort_values(
            "stemmed_word_freq", ascending=False
        ).head(TOP_N_WORDS)

        self._render_word_cloud_image(raw_words_freq_tab, output_path_raw_word_cloud)
        self._render_word_cloud_image(stemmed_words_freq_tab, output_path_stemmed_word_cloud)

        fig, ax = self._render_pandas_table(raw_words_freq_tab_filtered, header_columns=0, col_width=4.0)
        fig.savefig(output_path_top_raw_words)

        fig, ax = self._render_pandas_table(stemmed_words_freq_tab_filtered, header_columns=0, col_width=4.0)
        fig.savefig(output_path_top_stemmed_words)

    def generate_time_to_merge_info(self):
        """
        Generate table and plot showing relation between time to nearest
        merge in days and number of commits.
        """

        general_info_tab = self.all_tabs.get("general_info").dropna()
        output_path_tab = os.path.join(
            self.output_path, "time_to_merge_table.png"
        )
        output_path_plot = os.path.join(
            self.output_path, "time_to_merge_plot.png"
        )

        commit_merge_time = pd.DataFrame(
            {
                "commit_time": general_info_tab.commit_unix_time.apply(lambda x: datetime.fromtimestamp(x)),
                "merge_time": general_info_tab.merge_unix_time.apply(lambda x: datetime.fromtimestamp(x))
            }
        )

        output_tab = commit_merge_time.assign(
            days_to_merge=(commit_merge_time.merge_time - commit_merge_time.commit_time).dt.days
        ).groupby(
            "days_to_merge"
        ).agg(
            commits_number=("days_to_merge", "count")
        ).reset_index().sort_values(
            "days_to_merge", ascending=True
        ).head(TOP_N_DAYS_TIME_TO_MERGE)

        fig, ax = self._render_pandas_table(output_tab, header_columns=0, col_width=4.0)
        fig.savefig(output_path_tab)

        fig, ax = plt.subplots()
        sns.barplot(output_tab, x="days_to_merge", y="commits_number", ax=ax)
        plt.savefig(output_path_plot)

    @staticmethod
    def _generate_histogram(input_df: pd.DataFrame, col_name: str) -> None:
        """
        Generate histogram with mean and median value attached to it as
        black and orange lines respectively.

        :param input_df: data frame containing input data
        :param col_name: name of column storing variable to plot
        """

        # Set upper x lim to make the plot readable. It is calculated
        # as mean value of variable + x*standard deviation of variable
        # where 'x' comes from configuration file (SD_OUTLIERS_BORDER)
        mean_val = input_df[col_name].mean()
        std_val = input_df[col_name].std()
        median_val = input_df[col_name].median()
        max_val = mean_val + (SD_OUTLIERS_BORDER*std_val)
        input_df_filtered = input_df[input_df[col_name] < max_val]

        sns.displot(
            data=input_df_filtered, x=col_name, facet_kws=dict(sharey=False, sharex=False),
            bins=HISTOGRAM_BINS_NUM
        )

        plt.axvline(mean_val, c="k", ls='-', lw=2.5)
        plt.axvline(median_val, c="orange", ls='--', lw=2.5)

    def get_insertions_deletions_stats(self):
        """
        Get distribution of insertions and deletions per commit as histogram
        with mean and median value shown on it.
        """

        general_info_tab = self.all_tabs.get("general_info")
        output_path_insertions_hist = os.path.join(
            self.output_path, "insertions_histogram.png"
        )
        output_path_deletions_hist = os.path.join(
            self.output_path, "deletions_histogram.png"
        )
        output_path_insertions_tab = os.path.join(
            self.output_path, "insertions_stats.png"
        )
        output_path_deletions_tab = os.path.join(
            self.output_path, "deletions_stats.png"
        )

        insertions_summary = general_info_tab.insertions.describe().to_frame(
        ).reset_index().rename(columns={"index": "measure"}).round(2)
        deletions_summary = general_info_tab.deletions.describe().to_frame(
        ).reset_index().rename(columns={"index": "measure"}).round(2)

        fig, ax = self._render_pandas_table(insertions_summary, header_columns=0, col_width=4.0)
        fig.savefig(output_path_insertions_tab)

        fig, ax = self._render_pandas_table(deletions_summary, header_columns=0, col_width=4.0)
        fig.savefig(output_path_deletions_tab)

        self._generate_histogram(general_info_tab, "insertions")
        plt.savefig(output_path_insertions_hist)

        self._generate_histogram(general_info_tab, "deletions")
        plt.savefig(output_path_deletions_hist)

    def generate_all_plots_and_tables_for_given_report(self) -> None:
        """
        Generate all plots and tables required for single report
        """

        logger.info("Preparing report's tables and images for repo '{0}'".format(self.repo_name))

        logger.info("Preparing tables and plots showing peak times of contributions")
        self.generate_commits_time_of_day_table_and_plot()
        self.generate_commits_day_of_week_plot()

        logger.info("Preparing tables showing contributors activity and productivity")
        self.generate_contributors_activity_tables()

        logger.info("Preparing tables showing most frequent words in commit messages and word clouds")
        self.generate_word_clouds_imgs_and_tables()

        logger.info("Preparing tables and plots showing relation between number of commits and time to nearest merge")
        self.generate_time_to_merge_info()

        logger.info("Preparing plots showing distribution of insertions and deletions per commit")
        self.get_insertions_deletions_stats()