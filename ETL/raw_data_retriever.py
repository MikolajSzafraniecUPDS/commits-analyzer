"""
Class that can be used to extract raw commit data from the
repository
"""

import os
import subprocess
import re

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
    _OUTPUT_FILES = {
        "commits_hashes": "commits_hashes_no_merges.csv",
        "merges_info": "merges_info.csv",
        "commits_info": "commits_general_info.csv",
        "commits_messages": "commits_messages.csv",
        "insertions_deletions": "insertions_deletions.csv"
    }

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
            self.output_dir, self._OUTPUT_FILES.get("commits_hashes")
        )
        command = "git log --no-merges --all --pretty=format:'%H' > {0}".format(output_file)
        subprocess.run(command, shell=True)

    def _get_merges_info(self) -> None:
        """
        Get a list of hashes of merges commits and info
        about time of merge

        File will contain 2 columns:
            - Full commit hash
            - UNIX timestamp
        """

        output_file = os.path.join(
            self.output_dir, self._OUTPUT_FILES.get("merges_info")
        )
        command = "git log --merges --all --pretty=format:'%H;%at' > {0}".format(output_file)
        subprocess.run(command, shell=True)

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
            self.output_dir, self._OUTPUT_FILES.get("commits_info")
        )

        command = "git log --no-merges --all --pretty=format:{0} > {1}".format(
            self._GENERAL_INFO_FORMAT, output_file
        )

        subprocess.run(command, shell=True)

    def _get_commits_messages(self) -> None:
        """
        Get commits messages.

        Retrieval of commits messages can be quite challenging due to the
        fact that they can contain special characters, including column separators,
        such as comma or semicolon. In order to avoid parsing issues we will
        retrieve messages to a separate file, including only commits hashes as
        a form of primary key. We will use 'sed' command to delete all extra
        semicolon except the first one, separating hash from the message.

        Structure of the file:
            - Commit full hash
            - message
        """

        output_file = os.path.join(
            self.output_dir, self._OUTPUT_FILES.get("commits_messages")
        )
        # sed 's/;//2g' - replace all semicolons except the first one in each line with blank char
        command = "git log --merges --all --pretty=format:'%H;%s' | sed 's/;//2g' > {0}".format(
            output_file
        )
        subprocess.run(command, shell=True)

    @staticmethod
    def _extract_number_of_insertions_or_deletions_from_stats(
            pattern: str, commit_log: str
    ) -> int:
        """
        Helper function to '_get_insertions_deletions_info'. It retrieves
        number of insertion / deletions from given string and converts it to integer
        or returns zero if there were no match for given commit.

        :param pattern: regexp pattern to match
        :param commit_log: input string, results of 'git diff --stat HASH' call
        :return: number of insertions / deletions (depends on provided pattern)
        """

        regexp_match = re.search(pattern, commit_log)
        if regexp_match is None:
            res = 0
        else:
            res = int(regexp_match.group())

        return res

    @staticmethod
    def _get_git_diff_log(commit_hash: str) -> str:
        """
        Helper function to '_get_insertions_deletions_info'. It
        gets the git diff log for provided hash. We need only last line,
        which contains information which we are interested in.

        :param commit_hash: hash of the commit for which we want to get information
            about
        :return: full log in the form of string
        """

        command = "git diff --stat {0} | tail -n 1".format(commit_hash)
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output = str(proc.stdout.read())

        return output

    def _get_insertions_deletions_info(self, commit_hash: str) -> str:
        """
        Get a line containing info about insertions and deletions of single
        commit which is ready to append to the output file. Helper to the
        '_get_number_of_insertions_and_deletions_for_all_commits' function.

        :param commit_hash: hash of the commit we want to get info about
        :return: line separated with semicolons ready to append to the output
            .csv file
        """

        # Regexp patterns - find any number of digits followed by
        # ' insertion[s](+)' / ' deletion[s](-)' phrase
        REGEXP_PATTERN_INSERTIONS = r'[0-9]+(?= insertion[s]?\(\+\))'
        REGEXP_PATTERN_DELETIONS = r'[0-9]+(?= deletion[s]?\(\-\))'

        commit_log = self._get_git_diff_log(commit_hash)
        insertions = self._extract_number_of_insertions_or_deletions_from_stats(
            REGEXP_PATTERN_INSERTIONS, commit_log
        )
        deletions = self._extract_number_of_insertions_or_deletions_from_stats(
            REGEXP_PATTERN_DELETIONS, commit_log
        )

        output_line = "{0};{1};{2}".format(
            commit_hash, insertions, deletions
        )

        return output_line

    def _get_number_of_insertions_and_deletions_for_all_commits(self) -> None:
        """
        Get number of insertion and deletions for all commits. According to git
        documentation there is no such possibility to retrieve this information
        by log formatting, then we need to use 'git diff --stat' option and
        extract data with regexp.

        Structure of the output file:
            - Full hash of commit
            - Number of insertions per commit
            - Number of deletions per commit
        """

        commits_hashes_file_path = os.path.join(
            self.output_dir,
            self._OUTPUT_FILES.get("commits_hashes")
        )
        if not os.path.exists(commits_hashes_file_path):
            raise FileNotFoundError(
                "File containing list of hashes not created yet, repository: {0}".format(
                    self.repo_name
                )
            )

        with open(commits_hashes_file_path, 'r') as f:
            hashes_list = f.read().splitlines()

        output_file = os.path.join(
            self.output_dir, self._OUTPUT_FILES.get("insertions_deletions")
        )

        results = [
            self._get_insertions_deletions_info(commit_hash)
            for commit_hash in hashes_list
        ]

        with open(output_file, 'w') as f:
            f.writelines(results)

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
        self._get_commits_messages()
        self._get_number_of_insertions_and_deletions_for_all_commits()

        # Go back to the initial directory
        os.chdir(initial_dir)
