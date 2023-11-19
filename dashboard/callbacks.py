"""
Definitions of callbacsk functions fot the Dash applications. In order to
make the main app.py file more concise we will define callbacks generating
plots and tables in this separated file.
"""

import pandas as pd
import plotly.express as px

from dash.dash import Dash
from dash import Input, Output
from config.config import DB_TABLES_NAMES
from database.get_db_engine import get_db_engine
from config.config import TOP_N_CONTRIBUTORS_DASHBOARD

_ENGINE = get_db_engine()

def get_callbacks(app: Dash):
    """
    Definitions of callback functions for the Dash application

    :param app: Dash app object
    """

    # Generate commit timeline plot
    @app.callback(
        Output("commits-timeline-graph", "figure"),
        Input("repo_selector", "value")
    )
    def update_commits_timeline(repo_name: str):
        tab_name = DB_TABLES_NAMES.get("general_info").format(repo_name)
        sql_query = 'SELECT date_str, commit_hash FROM public."{0}"'.format(
            tab_name
        )
        df = pd.read_sql_query(sql_query, _ENGINE)
        df["date_dt"] = pd.to_datetime(df.date_str)
        df_agg = df.groupby("date_dt").agg(
            commits_num=("commit_hash", "count")
        ).reset_index()
        fig = px.line(df_agg, x="date_dt", y = "commits_num")
        return fig

    # Generate tables for top contributors tabs
    @app.callback(
        [
            Output("top-contributors-commits-volume", "data"),
            Output("top-contributors-insertions-volume", "data")
        ],
        Input("repo_selector", "value")
    )
    def update_top_contributors_tables(repo_name: str):
        tab_name = DB_TABLES_NAMES.get("authors_stats").format(repo_name)
        sql_query = 'SELECT author_name, number_of_insertions, number_of_commits FROM public."{0}"'.format(
            tab_name
        )
        df = pd.read_sql_query(sql_query, _ENGINE)

        top_commits_tab = df[["author_name", "number_of_commits"]].sort_values(
            "number_of_commits", ascending=False
        ).head(TOP_N_CONTRIBUTORS_DASHBOARD)

        top_insertions_tab = df[["author_name", "number_of_insertions"]].sort_values(
            "number_of_insertions", ascending=False
        ).head(TOP_N_CONTRIBUTORS_DASHBOARD)

        return top_commits_tab.to_dict("records"), top_insertions_tab.to_dict("records")
