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
from dashboard.tabs_components import render_commits_timeline_div

# Initialize the app
#external_stylesheets = [dbc.themes.CERULEAN]
#app = Dash("commits_analyzer", external_stylesheets=external_stylesheets)
app = Dash(__name__)

# Initialize some important variables
names_of_repos_to_analyze = get_names_of_availables_repos()

# App layout
app.layout = html.Div([
    html.H1(children='Commits Analyzer Dashboard'),
    dcc.Dropdown(
        names_of_repos_to_analyze,
        names_of_repos_to_analyze[0],
        id="repo_selector"
    ),
    dcc.Tabs(id="section-selection", value="commits-timeline", children=[
        dcc.Tab(label="Commits timeline", value="commits-timeline")#,
        #dcc.Tab(label="Top contributors", value="top-contributors")
    ]),
    html.Div(id="output-tab")
])

# Load callbacks definitions from external file
get_callbacks(app)

# Define a way of updating tabs of dashboard
@callback(
    Output("output-tab", "children"),
    Input("section-selection", "value")
)
def render_tab_content(tab_name: str):
    if tab_name == "commits-timeline":
        return render_commits_timeline_div()

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
