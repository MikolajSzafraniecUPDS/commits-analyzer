"""
Definitions of callbacsk functions fot the Dash applications
"""

import plotly.express as px

from dash.dash import Dash
from dash import Input, Output
from config.config import DB_TABLES_NAMES
import pandas as pd
from database.get_db_engine import get_db_engine

def get_callbacks(app: Dash):
    """
    Definitions of callback functions for the Dash application

    :param app: Dash app object
    """
    @app.callback(
        Output("commits-timeline-graph", "figure"),
        Input("repo_selector", "value")
    )
    def update_commits_timeline(repo_name: str):
        tab_name = DB_TABLES_NAMES.get("general_info").format(repo_name)
        sql_query = 'SELECT date_str, commit_hash FROM public."{0}"'.format(
            tab_name
        )
        engine = get_db_engine()
        df = pd.read_sql_query(sql_query, engine)
        df["date_dt"] = pd.to_datetime(df.date_str)
        df_agg = df.groupby("date_dt").agg(
            commits_num=("commit_hash", "count")
        ).reset_index()
        fig = px.line(df_agg, x="date_dt", y = "commits_num")
        return fig
