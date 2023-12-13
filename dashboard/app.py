"""
Dash application
"""

# Import packages
from dash import Dash, html, dcc, Input, Output, callback
from dashboard.utils import get_names_of_availables_repos
from dashboard.callbacks import get_callbacks
from dashboard.tabs_components import *
import dash_bootstrap_components as dbc

# Initialize the app
external_stylesheets = [dbc.themes.DARKLY]
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
    html.Br(),
    html.H2(children="Select repository:"),
    dbc.Select(
        names_of_repos_to_analyze,
        names_of_repos_to_analyze[0],
        id="repo_selector",
        style={"width": "20%"}
    ),
    html.Br(),
    html.Hr(),
    dbc.Tabs(
        id="section-selection",
        active_tab="commits-timeline",
        children=[
            dbc.Tab(label="Commits timeline", tab_id="commits-timeline"),
            dbc.Tab(label="Top contributors", tab_id="top-contributors"),
            dbc.Tab(label="Words frequency", tab_id="words-frequency"),
            dbc.Tab(label="Commits heatmap", tab_id="commits-heatmap"),
            dbc.Tab(label="Insertions distribution", tab_id="insertions-distributions")
        ]
    ),
    html.Div(id="output-tab")
])

# Define a way of updating tabs of dashboard
@callback(
    Output("output-tab", "children"),
    Input("section-selection", "active_tab")
)
def render_tab_content(tab_name: str) -> html.Div:
    """
    Render tab content dynamically. Such an approach is recommended
    due to the fact, that otherwise content for all tabs would be
    generated at the same moment, which could cause a performance
    issues.

    :param tab_name: id of tab to show
    """
    if tab_name == "commits-timeline":
        return render_commits_timeline_div()
    elif tab_name == "top-contributors":
        return render_top_contributors_div()
    elif tab_name == "words-frequency":
        return render_words_frequency_div()
    elif tab_name == "commits-heatmap":
        return render_commits_heatmap_tab()
    else:
        return render_insertions_distributions_tab()


# Load callbacks definitions from external file
get_callbacks(app)


# Run the app
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
