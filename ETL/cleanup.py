"""
Function which allows to delete repos after getting all needed data.
We don't want to store all analyzed repositories locally in order to
safe disc space - some of them might heavyweight.
"""

import subprocess
import os
import shutil
from pathlib import Path


class ReposDeletingError(Exception):
    """
    Exception raised in case when process of deleting repos
    is broken.
    """
    pass


def _delete_single_repo(repo_path: str) -> None:
    """
    Delete single repo stored as a submodule

    :param repo_path: path to the repository
    """
    # Remove submodule's directory
    subprocess.run(["git", "rm", f"{repo_path}"])
    # Commit changes
    subprocess.run(["git", "add", "."])
    subprocess.run(
        [
            "git", "commit", "-a", "-m",
            "'Submodule {0} removed'".format(os.path.basename(repo_path))
        ]
    )
    # In order to fully get rid of given submodule we need to manually
    # delete the submodule's directory in .git/modules/ and remove
    # the submodule's entry in the file .git/config
    subprocess.run(["rm", "-rf", ".git/modules/{}".format(repo_path)])
    subprocess.run(
        [
            "git", "config", "--remove-section",
            "submodule.{0}".format(repo_path)
        ]
    )


def delete_repos(repos_dir: str) -> None:
    """
    Fully delete all listed repos stored as submodules

    :param repos_dir: directory in which we store repos
        to analyze
    """

    try:
        repos_parent_dir = Path(repos_dir).parent.absolute()

        # Get relative paths to all repos in given dir
        repos_paths = [
            os.path.relpath(f.path, repos_parent_dir)
            for f in os.scandir(repos_dir) if f.is_dir()
        ]

        initial_dir = os.getcwd()
        os.chdir(repos_parent_dir)

        for repo_path in repos_paths:
            _delete_single_repo(repo_path)

        os.chdir(initial_dir)
    except Exception as e:
        raise ReposDeletingError(str(e))


def _clean_raw_files(raw_data_dir: str) -> None:
    """
    Clean raw .csv files after pipeline is finished

    :param raw_data_dir: raw data path from config
    """
    raw_data_dirs = [path for path in os.scandir(raw_data_dir) if path.is_dir()]
    for raw_dir in raw_data_dirs:
        shutil.rmtree(raw_dir)


def cleanup(repos_dir: str, raw_data_dir: str) -> None:
    """
    Final conducted in case of error - delete submodules and
    delete raw data.

    :param repos_dir: directory in which submodules are stored
    :param raw_data_dir: directory in which raw data is stored
    """

    delete_repos(repos_dir)
    _clean_raw_files(raw_data_dir)
