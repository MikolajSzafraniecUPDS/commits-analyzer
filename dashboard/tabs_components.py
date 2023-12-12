"""
Definitions of components for each tab of the dashboard.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table


def render_commits_timeline_div() -> html.Div:
    """
    Render content of dash tab showing commits timeline

    :return: output Dash Div
    """
    sidebar = html.Div(
        [
            html.Br(),
            html.H3("Commits timeline"),
            html.Hr(),
            html.P(
                """
                Plot showing number of commits per given period. 
                You can select time series granularity (daily / monthly).
                """,
                className="lead"
            ),
            dbc.Select(
                ["Day", "Month"],
                value="Day",
                id="timeline-agg-period"
            ),
        ]
    )

    res = html.Div([
        dbc.Row([
            dbc.Col(
                [
                    sidebar
                ],
                width=3
            ),
            dbc.Col([
                html.Br(),
                dcc.Graph(id="commits-timeline-graph")
            ])
        ])
    ])

    return res


def render_top_contributors_div() -> html.Div:
    """
    Render content for tab showing top contributors based on commit
    count and volume of insertions

    :return: output Dash Div
    """
    res = html.Div([
        html.Br(),
        html.H3("Top contributors"),
        html.Br(),
        html.P(
            """
            Tables presenting top contributors in terms of number of commits and number of insertions.
            """,
            className="lead"
        ),
        html.Br(),
        html.Div(
            children=dbc.Row(children=[
                dbc.Col([
                    html.H4("Top contributors in terms of commits count"),
                    html.Div(
                        id="top-contributors-commits-volume",
                        style={"maxHeight": "500px", "overflow": "scroll"}
                    )
                ]),
                dbc.Col([
                    html.H4("Top contributors in terms of volume of insertions"),
                    html.Div(
                        id="top-contributors-insertions-volume",
                        style={"maxHeight": "500px", "overflow": "scroll"}
                    )
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

    sidebar = html.Div([
        html.Br(),
        html.H3("Word frequency analysis"),
        html.P(
            """
            Table and wordcloud presenting key phrases most frequently used in commit
            messages.
            """,
            className="lead"
        ),
        html.Hr(),
        html.P(
            "Select type of the words to display (either 'raw' or 'stemmed'):", className="lead"
        ),
        dbc.Select(
            options=[
                {"label": "Raw words", "value": "raw"},
                {"label": "Stemmed words", "value": "stemmed"}
            ],
            value="raw",
            id="word-frequency-type"
        ),
        html.Br(),
        html.Hr(),
        html.H4("Word frequency table"),
        html.Div(
            id="word-frequency-tab",
            style={"maxHeight": "500px", "overflow": "scroll"}
        )
    ])

    res = html.Div([
        dbc.Row([
            dbc.Col(
                [
                    sidebar
                ],
                width=4
            ),
            dbc.Col([
                html.Br(),
                dbc.Row([
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

    sidebar = html.Div([
        html.Br(),
        html.H3("Commits heatmap"),
        html.P(
            "Plot showing number of insertions per day", className="lead"
        ),
        html.Hr(),
        html.P(
            "Please select commit author to show:", className="lead"
        ),
        dbc.Select(
            value="All",
            id="commits-author-to-heatmap"
        )
    ])

    res = html.Div([
        dbc.Row([
            dbc.Col(
                [
                    sidebar
                ],
                width=3
            ),
            dbc.Col([
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
        html.Br(),
        html.H3("Insertions stats"),
        html.P(
            """
            This tab presents histogram of number of insertions per single commit and general
            insertions stats.
            """,
            className="lead"
        ),
        html.Hr(),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H3("Distribution of number of insertions"),
                dcc.Graph(id="insertions-distributions-graph")
            ]),
            dbc.Col([
                html.H4("Insertions statistics"),
                html.Div(id="insertions-distribution-stats")
            ])
        ])
    ])

    return res
