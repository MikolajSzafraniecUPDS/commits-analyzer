"""
This file contains a list of repositories which we would like to analyze.
Please note that addresses should have a form of HTTPS urls to GitHub repo.
"""
REPOS_TO_ANALYZE = [
    "https://github.com/numpy/numpy",
    "https://github.com/DynamicTimeWarping/dtw-python",
    "https://github.com/boto/boto3"
]

# Directory in which we would like to store repos as submodules
# during the ETL process
SUBMODULES_DIR = "submodules"
