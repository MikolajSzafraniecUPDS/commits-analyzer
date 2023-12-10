"""
Dash application
"""

# Import packages
from dash import Dash, html, dcc, Input, Output, callback
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
        dcc.Tab(label="Words frequency", value="words-frequency"),
        dcc.Tab(label="Commits heatmap", value="commits-heatmap"),
        dcc.Tab(label="Insertions distribution", value="insertions-distributions")
    ]),
    html.Div(id="output-tab")
])

# Define a way of updating tabs of dashboard
@callback(
    Output("output-tab", "children"),
    Input("section-selection", "value")
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
