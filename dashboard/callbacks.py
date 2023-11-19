"""
Definitions of callbacsk functions fot the Dash applications. In order to
make the main app.py file more concise we will define callbacks generating
plots and tables in this separated file.
"""
import datetime

import pandas as pd
import plotly.express as px
import base64

from io import BytesIO

from dash.dash import Dash
from dash import Input, Output
from config.config import DB_TABLES_NAMES
from database.get_db_engine import get_db_engine
from config.config import TOP_N_CONTRIBUTORS_DASHBOARD, TOP_N_WORDS_DASHBOARD, DASHBOARD_SD_OUTLIERS_BORDER
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
        [
            Input("repo_selector", "value"),
            Input("timeline-agg-period", "value")
        ]
    )
    def update_commits_timeline(repo_name: str, agg_period: str):
        """
        Update plot showing commit timeline in the form of time series

        :param repo_name: name of selected repository
        :param agg_period: aggregation period - might be a day or month
        """
        tab_name = DB_TABLES_NAMES.get("general_info").format(repo_name)
        sql_query = 'SELECT date_str, commit_hash FROM public."{0}"'.format(
            tab_name
        )
        df = pd.read_sql_query(sql_query, _ENGINE)
        df["date_dt"] = pd.to_datetime(df.date_str)
        if agg_period == "Day":
            df_agg = df.groupby("date_dt").agg(
                commits_num=("commit_hash", "count")
            ).reset_index()
        else:
            df_agg = df.assign(
                date_dt=pd.to_datetime(df.date_str).dt.strftime("%Y-%m")
            ).groupby(
                "date_dt"
            ).agg(
                commits_num=("commit_hash", "count")
            ).reset_index()

            df_agg["date_dt"] = pd.to_datetime(df_agg.date_dt)

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
        """
        Update tables presenting top contributors based on number of insertions
        and number of commits

        :param repo_name: name of selected repository
        """
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
        """
        Update word cloud plot and table presenting word frequency in commit
        messages.

        :param repo_name: name of selected repository
        :param word_type: type of words to analyze (either 'raw' or 'stemmed')
        """
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

    @app.callback(
        [
            Output("commits-author-to-heatmap", "options"),
            Output("commits-author-to-heatmap", "value")
        ],
        Input("repo_selector", "value")
    )
    def update_commits_authors_dropdown(repo_name):
        """
        Update dropdown allowing to select commit author

        :param repo_name: name of selected repository
        """
        tab_name = DB_TABLES_NAMES.get("general_info").format(repo_name)
        sql_query = 'SELECT DISTINCT author_name FROM public."{0}"'.format(
            tab_name
        )
        df = pd.read_sql_query(sql_query, _ENGINE)
        res = ["All"] + df.author_name.to_list()
        return res, "All"

    def _generate_heatmap_data(date_df: pd.DataFrame, dates_range: pd.DatetimeIndex) -> pd.DataFrame:
        """
        Transform pandas dataframe containing column denoting date of a
        commit to dataframe suitable for heatmap needs.

        :param date_df: input DataFrame containing single column 'date_str'
            in format "%Y-%m-%d"
        :param date_range: date range to plot the heatmap
        :return: DataFrame suitable for heatmap, with weekdays in rows and
            year + number of week in column
        """

        df_commits_count_added = date_df.groupby("date_str").agg(
            commits_count=("date_str", "count")
        )

        # Transform index to DateTime
        df_commits_count_added.index = pd.DatetimeIndex(df_commits_count_added.index)

        # Fill missing dates where there was no single commit with zeros
        df_reindexed = df_commits_count_added.reindex(dates_range, fill_value=0)

        # Get weekday and year+week number, pivot table to final form
        res = df_reindexed.assign(
            year_week=df_reindexed.index.strftime("%Y-%W"),
            weekday=df_reindexed.index.isocalendar().day
        ).pivot_table(
            values="commits_count",
            index="weekday",
            columns="year_week",
            fill_value=0
        )

        return res

    def _get_date_range_from_db(repo_name: str) -> pd.DatetimeIndex:
        """
        Get date range as min and max dates for given repo directly
        from database

        :param repo_name: name of the repository
        :return: date range in the form of DateTimeIndex object
        """
        tab_name = DB_TABLES_NAMES.get("general_info").format(repo_name)

        sql_min_date = 'SELECT MIN(TO_DATE(date_str, \'YYYY-MM-DD\')) FROM public."{0}"'.format(tab_name)
        sql_max_date = 'SELECT MAX(TO_DATE(date_str, \'YYYY-MM-DD\')) FROM public."{0}"'.format(tab_name)

        min_date_val = pd.read_sql_query(sql_min_date, _ENGINE).iloc[0, 0]
        max_date_val = pd.read_sql_query(sql_max_date, _ENGINE).iloc[0, 0]

        res = pd.date_range(min_date_val, max_date_val)

        return res

    @app.callback(
        Output("commits-heatmap", "figure"),
        [
            Input("repo_selector", "value"),
            Input("commits-author-to-heatmap", "value")
        ]
    )
    def update_commits_heatmap(repo_name, author_name):
        """
        Update plot showing number of commits across time in the form
        of heatmap.

        :param repo_name: name of selected repository
        :param author_name: name of author to plot ('All' as default)
        """
        tab_name = DB_TABLES_NAMES.get("general_info").format(repo_name)
        sql_query = 'SELECT date_str FROM public."{0}"'.format(tab_name)
        if author_name != "All":
            sql_query += " WHERE author_name = \'{0}\'".format(author_name)

        d_range = _get_date_range_from_db(repo_name)

        df = pd.read_sql_query(sql_query, _ENGINE)
        df_prepared = _generate_heatmap_data(df, d_range)

        fig = px.imshow(
            df_prepared,
            color_continuous_scale="Greens"
        )

        fig.layout.height = 400
        return fig

    def _generate_histogram_of_insertions(input_df: pd.DataFrame):
        """
        Generate histogram showing distribution of number of insertions
        across commits

        :param input_df: data frame containing input data
        :param col_name: name of column storing variable to plot
        """

        # Set upper x lim to make the plot readable. It is calculated
        # as mean value of variable + x*standard deviation of variable
        # where 'x' comes from configuration file (SD_OUTLIERS_BORDER)
        mean_val = input_df["insertions"].mean()
        std_val = input_df["insertions"].std()
        max_val = mean_val + (DASHBOARD_SD_OUTLIERS_BORDER*std_val)
        input_df_filtered = input_df[input_df["insertions"] < max_val]

        fig = px.histogram(
            input_df_filtered,
            x="insertions",
            nbins=20
        )

        return fig

    @app.callback(
        [
            Output("insertions-distributions-graph", "figure"),
            Output("insertions-distribution-stats", "data")
        ],
        Input("repo_selector", "value")
    )
    def update_commits_distribution_graph_and_table(repo_name):
        """
        Update plot presenting distribution of insertions across commits and
        table showing insertions statistics.

        :param repo_name: name of selected repository
        """
        tab_name = DB_TABLES_NAMES.get("general_info").format(repo_name)
        sql_query = 'SELECT commit_hash, insertions FROM public."{0}"'.format(
            tab_name
        )
        df = pd.read_sql_query(sql_query, _ENGINE)

        histogram_fig = _generate_histogram_of_insertions(df)
        insertions_stats = df.insertions.describe().to_frame(
        ).reset_index().rename(
            columns={"index": "Measure", "insertions": "Insertions"}
        ).round(2)

        return histogram_fig, insertions_stats.to_dict("records")
