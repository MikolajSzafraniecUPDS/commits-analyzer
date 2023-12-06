"""
Definition of process of getting repositories as submodules this repo.
"""

import subprocess
import os
from typing import List


class GetReposError(Exception):
    """
    Exception raised in case when process of getting repos
    is broken.
    """
    pass


def _store_single_repo_as_submodule(repo_url: str) -> None:
    """
    Clone chosen repository as a submodule. We use submodule
    because we would like to keep the analyzed repos as separated
    instances - it will simplify the process of retrieving commits
    logs.

    :param repo_url: HTTPS url to the repository we want to clone as
        a submodule
    """
    subprocess.run(["git", "submodule", "add", f'{repo_url}'])
    subprocess.run(
        [
            "git", "commit", "-a", "-m",
            "'Submodule {0} cloned'".format(os.path.basename(repo_url))
        ]
    )


def get_repos(repos_list: List[str], submodules_dir: str) -> None:
    """
    Clone all repositories specified in the configuration file as
    submodules.

    :param repos_list: List of HTTPS urls to the repositories we want
        to analyze
    :param submodules_dir: directory in which we are going to store
        repos during ETL process
    """
    try:
        initial_dir = os.getcwd()
        os.chdir(submodules_dir)

        for repo_url in repos_list:
            _store_single_repo_as_submodule(repo_url)

        os.chdir(initial_dir)
    except Exception as e:
        raise GetReposError(str(e))
