"""
Definition of process of getting repositories as submodules this repo.
"""

import subprocess
import os

# A way to fix import errors
try:
    from config.repos_to_analyze import REPOS_TO_ANALYZE
except ImportError:
    import sys
    sys.path.append(sys.path[0] + '/..')
    from config.repos_to_analyze import REPOS_TO_ANALYZE

from config.repos_to_analyze import REPOS_TO_ANALYZE


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


def get_repos() -> None:
    """
    Clone all repositories specified in the configuration file as
    submodules.
    """

    for repo_url in REPOS_TO_ANALYZE:
        _store_single_repo_as_submodule(repo_url)


if __name__ == "__main__":
    get_repos()