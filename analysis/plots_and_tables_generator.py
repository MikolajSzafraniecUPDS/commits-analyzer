"""
Tools responsible for generating plots and tables for
the purpose of analysis
"""

import os
import pandas as pd
import seaborn as sns
import numpy as np

from config.db_tables_config import DB_TABLES_NAMES
from typing import Dict
from sqlalchemy import Engine
from config.paths import ANALYSIS_RESULTS_DIR
from typing import List

import matplotlib.pyplot as plt


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

