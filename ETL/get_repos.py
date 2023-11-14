"""
Definition of process of getting repositories as submodules this repo.
"""

import subprocess
import os
from typing import List

def _store_single_repo_as_submodule(repo_url: str) -> None:
    """
    Clone chosen repository as a submodule. We use submodule
    because we would like to keep the analyzed repos as separated
    instances - it will simplify the process of retrieving commits
    logs.

    :param repo_url: HTTPS url to the repository we want to clone as
        a submodule
    """
    os.chdir("submodules")
    subprocess.run(["git", "submodule", "add", f'{repo_url}'])
    os.chdir("..")


def get_repos(repos_list: List[str]) -> None:
    """
    Clone all repositories specified in the configuration file as
    submodules.

    :param repos_list: List of HTTPS urls to the repositories we want
        to analyze
    """

    for repo_url in repos_list:
        _store_single_repo_as_submodule(repo_url)
