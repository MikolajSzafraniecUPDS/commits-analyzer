"""
Definitions of components for each tab of the dashboard
"""

from dash import dcc, html


def render_commits_timeline_div():
    """
    Render content of dash tab showing commits timeline
    :return:
    """
    res = html.Div([
        html.H3("Commits timeline"),
        dcc.Graph(id="commits-timeline-graph")
    ])

    return res

def render_top_contributors_div():
    pass