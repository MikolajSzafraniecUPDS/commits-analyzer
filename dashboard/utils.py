"""
A set of basic functions simplifying work with dashboard
"""

import os
from config.config import REPOS_TO_ANALYZE


def get_names_of_availables_repos():
    """
    Get names of repositories to analyze based on the config
    file.
    """

    res = [
        os.path.basename(f)
        for f in REPOS_TO_ANALYZE
    ]

    return res
