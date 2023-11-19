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
    res = html.Div([
        html.H3("Commits timeline"),
        dcc.Graph(id="commits-timeline-graph")
    ])

    return res

def render_top_contributors_div() -> html.Div:
    """
    Render content for tab showing top contributors based on commit
    count and volume of insertions

    :return:
    """
    res = html.Div([
        html.H3("Top contributors"),
        dbc.Row([
            dbc.Col([
                html.H4("Top contributors in terms of commits count"),
                dash_table.DataTable(id="top-contributors-commits-volume")
            ]),
            dbc.Col([
                html.H4("Top contributors in terms of volume of insertions"),
                dash_table.DataTable(id="top-contributors-insertions-volume")
            ])
        ])
    ])

    return res