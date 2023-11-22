"""
Configuration file
"""

### REPOSITORY TO ANALYZE
# This section contains a list of repositories which we would like to analyze.
# Please note that addresses should have a form of HTTPS urls to GitHub repo.

REPOS_TO_ANALYZE = [
    "https://github.com/numpy/numpy",
    "https://github.com/DynamicTimeWarping/dtw-python",
    "https://github.com/boto/boto3"
]

### DATABASE CREDENTIALS
# Postgres database credentials - it has to be the same as in
# docker/env_variables/global.env and .env files
POSTGRES_HOST = "127.0.0.1"
POSTGRES_HOST_COMPOSE = "db"
POSTGRES_PORT = "5432"
POSTGRES_DB = "commits_analyzer"
POSTGRES_USER = "commits_analyzer"
POSTGRES_PASSWORD = "gheJasl34asFD"

### CONFIGURATION OF RAW .CSV FILES
# Format of file containing general information
GENERAL_INFO_FORMAT = "'%H;%ae;%an;%at;%ce;%cn'"

# Names of output files
OUTPUT_FILES = {
    "commits_hashes": "commits_hashes_no_merges.csv",
    "merges_info": "merges_info.csv",
    "commits_info": "commits_general_info.csv",
    "commits_messages": "commits_messages.csv",
    "insertions_deletions": "insertions_deletions.csv"
}

# Files headers
HEADERS = {
    "commits_hashes": ["commit_hash"],
    "merges_info": ["merge_hash", "merge_unix_time"],
    "commits_info": [
        "commit_hash",
        "author_email",
        "author_name",
        "commit_unix_time",
        "commiter_email",
        "commiter_name"
    ],
    "commits_messages": ["commit_hash", "commit_message"],
    "insertions_deletions": ["commit_hash", "insertions", "deletions"]
}

### POSTGRES TABLES NAMES
# Names of postgres databases
DB_TABLES_NAMES = {
    "general_info": "{0}_general_commits_info",
    "authors_stats": "{0}_authors_stats",
    "messages_all_words": "{0}_messages_all_words",
    "messages_raw_words_freq": "{0}_messages_raw_words_freq",
    "messages_stemmed_words_freq": "{0}_messages_stemmed_words_freq"
}

### LOCAL PATHS
# Directory in which we would like to store repos as submodules
# during the ETL process
SUBMODULES_DIR = "submodules"

# Directory in which we would like to store raw .csv files during the
# ETL process
RAW_DATA_DIR = "raw_data"

# Directory in which analysis results will be saved
ANALYSIS_RESULTS_DIR = "results"

### CONFIGURATION OF OUTPUT REPORTS
# How many top n contributors show in the tables summarizing contributors activity
# and productivity
TOP_N_CONTRIBUTORS: int = 10

# Minimal number of insertions and deletions for insertions / deletions ratio stats - for contributors with
# low activity number are exceptionally high (for example 5 insertions and 0 deletions the ratio
# is infinite)
MIN_INSERTIONS = 50
MIN_DELETIONS = 10

# How many top words show in the words frequency tables
TOP_N_WORDS = 15

# How many top n days shows in the table summarizing relation
# between number of commits and time to nearest merge
TOP_N_DAYS_TIME_TO_MERGE = 20

# Insertions deletions outliers border as number of standard
# deviations added to the mean value
SD_OUTLIERS_BORDER = 3

# Number of bins for histograms showing number of insertions and
# deletions. Set 'auto' if you would like seaborn to set it
# in an automated way
HISTOGRAM_BINS_NUM = 50

### DASHBOARD CONFIG
# Number of top n contributors in terms of commits and insertions volume
# to show in dashboard tables
TOP_N_CONTRIBUTORS_DASHBOARD = 20

# Number of top n words to show in pattern analysis
TOP_N_WORDS_DASHBOARD = 25

# Insertions deletions outliers border as number of standard
# deviations added to the mean value
DASHBOARD_SD_OUTLIERS_BORDER = 1

# Dash port
DASH_PORT = 8050

# Flag indicating whether to automatically open a browser when
# launching an app
LAUNCH_BROWSER = True

### PIPELINE CONFIGURATION

# Clean /raw_data directory after pipeline is finished?
CLEAN_RAW_DATA = True

# Launch dashboard at the end of pipeline
RUN_DASHBOARD = True
