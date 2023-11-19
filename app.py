"""
Dash application
"""

# Import packages
import pandas as pd
import dash_bootstrap_components as dbc

from dash import Dash, html, dcc, Input, Output, callback
from database.get_db_engine import get_db_engine
from dashboard.utils import get_names_of_availables_repos
from dashboard.callbacks import get_callbacks
from dashboard.tabs_components import *


# Initialize the app
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = Dash(
    "commits_analyzer",
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True  # We generate tab content dynamically, so this flag must be set as True
)

# Initialize some important variables
names_of_repos_to_analyze = get_names_of_availables_repos()

# App layout
app.layout = html.Div([
    html.H1(children='Commits Analyzer Dashboard'),
    html.H2(children="Select repository:"),
    dcc.Dropdown(
        names_of_repos_to_analyze,
        names_of_repos_to_analyze[0],
        id="repo_selector"
    ),
    dcc.Tabs(id="section-selection", value="commits-timeline", children=[
        dcc.Tab(label="Commits timeline", value="commits-timeline"),
        dcc.Tab(label="Top contributors", value="top-contributors"),
        dcc.Tab(label="Words frequency", value="words-frequency")
    ]),
    html.Div(id="output-tab")
])

# Define a way of updating tabs of dashboard
@callback(
    Output("output-tab", "children"),
    Input("section-selection", "value")
)
def render_tab_content(tab_name: str):
    if tab_name == "commits-timeline":
        return render_commits_timeline_div()
    elif tab_name == "top-contributors":
        return render_top_contributors_div()
    elif tab_name == "words-frequency":
        return render_words_frequency_div()


# Load callbacks definitions from external file
get_callbacks(app)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
