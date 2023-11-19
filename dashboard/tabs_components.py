"""
Definitions of components for each tab of the dashboard.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from database.get_db_engine import get_db_engine
from typing import List


def render_commits_timeline_div() -> html.Div:
    """
    Render content of dash tab showing commits timeline

    :return: output Dash Div
    """
    res = html.Div([
        html.H3("Commits timeline"),
        dcc.Graph(id="commits-timeline-graph")
    ])

    return res


def render_top_contributors_div() -> html.Div:
    """
    Render content for tab showing top contributors based on commit
    count and volume of insertions

    :return: output Dash Div
    """
    res = html.Div([
        html.H3("Top contributors"),
        html.Div(
            children=dbc.Row(children=[
                dbc.Col([
                    html.H4("Top contributors in terms of commits count"),
                    dash_table.DataTable(id="top-contributors-commits-volume", fill_width=False)
                ]),
                dbc.Col([
                    html.H4("Top contributors in terms of volume of insertions"),
                    dash_table.DataTable(id="top-contributors-insertions-volume", fill_width=False)
                ])
            ])
        )
    ])

    return res


def render_words_frequency_div() -> html.Div:
    """
    Render tab containing word frequency analysis (word cloud
    and word frequency table).

    :return: output Dash Div
    """

    res = html.Div([
        html.H3("Word frequency analysis"),
        dcc.Dropdown(
            options=[
                {"label": "Raw words", "value": "raw"},
                {"label": "Stemmed words", "value": "stemmed"}
            ],
            value="raw",
            id="word-frequency-type"
        ),
        dbc.Row([
            dbc.Col([
                html.H4("Word cloud"),
                html.Img(
                    id="word-cloud-image",
                    style={
                        "display": "block",
                        "margin-left": "auto",
                        "margin-right": "auto",
                        "width": "90%"
                    }
                )
            ]),
            dbc.Col([
                html.H4("Word frequency table"),
                dash_table.DataTable(
                    id="word-frequency-tab",
                    fill_width=False
                )
            ])
        ])
    ])

    return res


def render_commits_heatmap_tab() -> html.Div:
    """
    Render tab containing heatmap presenting number of commits
    per day.

    :return: output Dash Div
    """
    res = html.Div([
        html.H3("Commits heatmap"),
        dbc.Row([
            dbc.Col([
                html.H4("Select commit author"),
                dcc.Dropdown(
                    value="All",
                    id="commits-author-to-heatmap"
                ),
                dcc.Graph(id="commits-heatmap")
            ]),
        ])
    ])

    return res


def render_insertions_distributions_tab() -> html.Div:
    """
    Render tab containing visualization of number of insertions
    across all commits in the form of histogram.

    :return: output Dash Div
    """

    res = html.Div([
        html.H3("Distribution of number of insertions"),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="insertions-distributions-graph")
            ]),
            dbc.Col([
                dash_table.DataTable(
                    id="insertions-distribution-stats",
                    fill_width=False
                )
            ])
        ])
    ])

    return res
