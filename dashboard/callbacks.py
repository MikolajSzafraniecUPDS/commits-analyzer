"""
Definitions of callbacsk functions fot the Dash applications. In order to
make the main app.py file more concise we will define callbacks generating
plots and tables in this separated file.
"""

import pandas as pd
import plotly.express as px
import base64

from io import BytesIO

from dash.dash import Dash
from dash import Input, Output
from config.config import DB_TABLES_NAMES
from database.get_db_engine import get_db_engine
from config.config import TOP_N_CONTRIBUTORS_DASHBOARD, TOP_N_WORDS_DASHBOARD
from wordcloud import WordCloud

_ENGINE = get_db_engine()


def _render_word_cloud_image(freq_table: pd.DataFrame):
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
    #wordcloud.generate_from_frequencies(frequencies=frequencies_dict)
    wordcloud.fit_words(frequencies_dict)
    return wordcloud.to_image()


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
        ).head(TOP_N_CONTRIBUTORS_DASHBOARD).rename(
            columns={
                "author_name": "Contributor name",
                "number_of_commits": "Number of commits"
            }
        )

        top_insertions_tab = df[["author_name", "number_of_insertions"]].sort_values(
            "number_of_insertions", ascending=False
        ).head(TOP_N_CONTRIBUTORS_DASHBOARD).rename(
            columns={
                "author_name": "Contributor name",
                "number_of_insertions": "Number of insertions"
            }
        )

        return top_commits_tab.to_dict("records"), top_insertions_tab.to_dict("records")

    @app.callback(
        [
            Output("word-cloud-image", "src"),
            Output("word-frequency-tab", "data")
        ],
        [
            Input("repo_selector", "value"),
            Input("word-frequency-type", "value")
        ]
    )
    def update_word_cloud_and_word_freq_table(repo_name: str, word_type: str):
        if word_type == "raw":
            tab_name = DB_TABLES_NAMES.get("messages_raw_words_freq").format(repo_name)
            word_col_name = "raw_word"
            freq_col_name = "raw_word_freq"
        else:
            tab_name = DB_TABLES_NAMES.get("messages_stemmed_words_freq").format(repo_name)
            word_col_name = "stemmed_word"
            freq_col_name = "stemmed_word_freq"
        sql_query = 'SELECT {0}, {1} FROM public."{2}"'.format(
            word_col_name,
            freq_col_name,
            tab_name
        )
        df = pd.read_sql_query(sql_query, _ENGINE)

        img = BytesIO()
        _render_word_cloud_image(df).save(img, format="PNG")
        image_src = 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

        output_tab = df.sort_values(
            freq_col_name, ascending=False
        ).head(TOP_N_WORDS_DASHBOARD).rename(
            columns={
                word_col_name: "Word",
                freq_col_name: "Frequency"
            }
        )

        return image_src, output_tab.to_dict("records")
