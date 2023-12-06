"""
Function which allows to delete repos after getting all needed data.
We don't want to store all analyzed repositories locally in order to
safe disc space - some of them might heavyweight.
"""

import subprocess
import os


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

    # Get paths to all repos in given dir
    repos_paths = [
        os.path.abspath(f.path)
        for f in os.scandir(repos_dir) if f.is_dir()
    ]

    initial_dir = os.getcwd()
    os.chdir(repos_dir)

    for repo_path in repos_paths:
        _delete_single_repo(repo_path)

    os.chdir(initial_dir)
