"""
Class that can be used to extract raw commit data from the
repository
"""

import os
import subprocess

from pathlib import Path


class RawDataRetriever:

    """
    This class retrieves the set of raw commits data from target repository
    (stored as submodule) and save it in the output directory.
    """

    # Format of output file for commits general info, which includes:
    # - Commit full hash
    # - Author email
    # - Author name
    # - UNIX timestamp
    # - Committer email
    # - Committer name
    # - Encoding
    #
    # More info about git log formatting: https://git-scm.com/docs/pretty-formats
    _GENERAL_INFO_FORMAT = "'%H;%ae;%an;%at;%ce;%cn;%e'"

    def __init__(self, repo_path: str, output_dir: str):
        """
        Initialize an instance of the class

        :param repo_path: path to the repository
        :param output_dir: directory in which results will be kept
        """
        self.repo_path = repo_path
        self.repo_name = os.path.basename(repo_path)
        # We need an absolute path of the output directory
        self.output_dir = os.path.join(os.path.abspath(output_dir), self.repo_name)

    def _get_commit_hashes_no_merges(self) -> None:
        """
        Get a list of hashes of all commits except merges
        and store them in the .csv file
        """

        output_file = os.path.join(
            self.output_dir, "no_merge_hashes.csv"
        )
        command = [
            "git", "log", "--no-merges",
            "--all", "--pretty=format:'%H'"
        ]

        with open(output_file, 'w') as f:
            subprocess.run(command, stdout=f)

    def _get_merges_info(self) -> None:
        """
        Get a list of hashes of merges commits and info
        about time of merge

        File will contain 2 columns:
            - Full commit hash
            - UNIX timestamp
        """

        output_file = os.path.join(
            self.output_dir, "merges_info.csv"
        )
        command = [
            "git", "log", "--merges",
            "--all", "--pretty=format:'%H;%at'"
        ]

        with open(output_file, 'w') as f:
            subprocess.run(command, stdout=f)

    def _get_commits_general_info(self) -> None:
        """
        Get general info about commit and save it to the .csv
        file. It will contain following columns:
        - Commit full hash
        - Author email
        - Author name
        - UNIX timestamp
        - Committer email
        - Committer name
        - Encoding
        """

        output_file = os.path.join(
            self.output_dir, "commits_general_info.csv"
        )
        command = [
            "git", "log", "--merges",
            "--all", "--pretty=format:" + self._GENERAL_INFO_FORMAT
        ]

        with open(output_file, 'w') as f:
            subprocess.run(command, stdout=f)

    def generate_raw_data(self):
        # Get current working directory
        initial_dir = os.getcwd()

        # Create output directory
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        # Go to the repo dir and generate data
        os.chdir(self.repo_path)
        self._get_commit_hashes_no_merges()
        self._get_merges_info()
        self._get_commits_general_info()

        # Go back to the initial directory
        os.chdir(initial_dir)
