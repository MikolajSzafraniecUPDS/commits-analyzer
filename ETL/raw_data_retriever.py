"""
Class that can be used to extract raw commit data from the
repository
"""

import os
import subprocess
import logging.config

from pathlib import Path
from typing import List

logging.config.fileConfig(os.path.join("config", "logging.conf"))
logger = logging.getLogger("consoleLogger")

class RawDataRetriever:

    """
    This class retrieves the set of raw commits data from target repository
    (stored as submodule) and save it in the output directory.

    List of the files is as follows:
        - commits_hashes_no_merges.csv - list of hashes of all commits except merges; we
            will use it later as a primary key in database
        - commits_general_info.csv - general info regarding commits, such as author, time
            and commiter
        - commits_messages.csv - list of all commits messages
        - insetions_deletions.csv - number of insertions and deletions for each commit
        - merges_info.csv - hashes and time of merges, we will use it in the analysis
    """

    # Format of output file for commits general info, which includes:
    # - Commit full hash
    # - Author email
    # - Author name
    # - UNIX timestamp
    # - Committer email
    # - Committer name
    #
    # More info about git log formatting: https://git-scm.com/docs/pretty-formats
    _GENERAL_INFO_FORMAT = "'%H;%ae;%an;%at;%ce;%cn'"
    _OUTPUT_FILES = {
        "commits_hashes": "commits_hashes_no_merges.csv",
        "merges_info": "merges_info.csv",
        "commits_info": "commits_general_info.csv",
        "commits_messages": "commits_messages.csv",
        "insertions_deletions": "insertions_deletions.csv"
    }
    # File headers
    _HEADERS = {
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


    def _generate_headers(self, file_type: str) -> str:
        """
        Generate headers line for given file based using _HEADERS
        dictionary.

        :param file_type: type of the file (one of keys from _HEADERS dict)
        :return: headers line, separated with semicolon with '\n' at the end
        """

        res = ";".join(self._HEADERS.get(file_type)) + "\n"
        return res

    def _get_commit_hashes_no_merges(self) -> None:
        """
        Get a list of hashes of all commits except merges
        and store them in the .csv file
        """

        output_file = os.path.join(
            self.output_dir, self._OUTPUT_FILES.get("commits_hashes")
        )

        headers = self._generate_headers("commits_hashes")
        with open(output_file, 'w') as f:
            f.write(headers)

        command = "git log --no-merges --all --pretty=format:'%H' >> {0}".format(output_file)
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

        headers = self._generate_headers("merges_info")
        with open(output_file, 'w') as f:
            f.write(headers)

        command = "git log --merges --all --pretty=format:'%H;%at' >> {0}".format(output_file)
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
        """

        output_file = os.path.join(
            self.output_dir, self._OUTPUT_FILES.get("commits_info")
        )

        headers = self._generate_headers("commits_info")
        with open(output_file, 'w') as f:
            f.write(headers)

        command = "git log --no-merges --all --pretty=format:{0} >> {1}".format(
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

        headers = self._generate_headers("commits_messages")
        with open(output_file, 'w') as f:
            f.write(headers)

        # sed 's/;//2g' - replace all semicolons except the first one in each line with blank char
        command = "git log --no-merges --all --pretty=format:'%H;%s' | sed 's/;//2g' >> {0}".format(
            output_file
        )
        subprocess.run(command, shell=True)

    @staticmethod
    def _get_git_diff_log(commit_hash: str) -> List[str]:
        """
        Helper function to '_get_insertions_deletions_info'. It
        gets the stats for provided hash. We need only last line,
        which contains information which we are interested in (insertions
        and deletions). Line is split into list of words.

        :param commit_hash: hash of the commit for which we want to get information
            about
        :return: last line of the log containing information about number of insertions
            and deletions, split to the form of list of words
        """

        command = "git show --shortstat {0} | tail -n 1".format(commit_hash)
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output = proc.stdout.read().decode().split()

        return output

    @staticmethod
    def _extract_number_of_insertions(
            log_line: List[str]
    ) -> int:
        """
        Helper function to '_get_insertions_deletions_info'. It retrieves
        number of insertion from last line of git diff log converted to
        list of strings.

        :param log_line: last line of git diff log, decoded and converted to list
            of words
        :return: number of insertions per commit
        """

        # Helper internals
        def _both_insertions_and_deletions() -> bool:
            return len(log_line) == 7

        def _insertions_only() -> bool:
            return log_line[4].startswith("insert")

        if _both_insertions_and_deletions():  # Case when there are both insertions and deletions
            res = int(log_line[3])
        else:
            res = int(log_line[3]) if _insertions_only() else 0

        return res

    @staticmethod
    def _extract_number_of_deletions(
            log_line: List[str]
    ) -> int:
        """
        Helper function to '_get_insertions_deletions_info'. It retrieves
        number of deletions from last line of git diff log converted to
        list of strings.

        :param log_line: last line of git diff log, decoded and converted to list
            of words
        :return: number of deletions per commit
        """

        # Helper internals
        def _both_insertions_and_deletions() -> bool:
            return len(log_line) == 7

        def _insertions_only() -> bool:
            return log_line[4].startswith("insert")

        if _both_insertions_and_deletions():  # Case when there are both insertions and deletions
            res = int(log_line[5])
        else:
            res = 0 if _insertions_only() else int(log_line[5])

        return res

    def _get_insertions_deletions_info(self, commit_hash: str) -> str:
        """
        Get a line containing info about insertions and deletions of single
        commit which is ready to append to the output file. Helper to the
        '_get_number_of_insertions_and_deletions_for_all_commits' function.

        :param commit_hash: hash of the commit we want to get info about
        :return: line separated with semicolons ready to append to the output
            .csv file
        """

        commit_log = self._get_git_diff_log(commit_hash)
        if not commit_log:  # Case when there are no insertions nor deletions
            insertions = 0
            deletions = 0
        else:
            try:
                insertions = self._extract_number_of_insertions(commit_log)
                deletions = self._extract_number_of_deletions(commit_log)
            except Exception as e: # In case there are any unpredictable exception we need to assume that number of insertions and deletions are zeros
                insertions = 0
                deletions = 0

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
            self._get_insertions_deletions_info(commit_hash) + "\n"
            for commit_hash in hashes_list[1:]  # Skip header
        ]

        headers = self._generate_headers("insertions_deletions")
        results.insert(0, headers)

        with open(output_file, 'w') as f:
            f.writelines(results)

    def generate_raw_data(self):
        """
        Generate all files containing raw commits data for given repository.
        """
        repo_name = os.path.basename(self.repo_path)
        logger.info("Process of generating raw commits data for repo '{0}' started".format(repo_name))

        # Get current working directory
        initial_dir = os.getcwd()

        # Create output directory
        logger.info("Creating output directory to store raw data for repo '{0}'".format(repo_name))
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        # Go to the repo dir and generate data
        logger.info("Changing dir to repository dir")
        os.chdir(self.repo_path)
        logger.info("Generating commits hashes for repo '{0}'".format(repo_name))
        self._get_commit_hashes_no_merges()
        logger.info("Generating merges info for repo '{0}'".format(repo_name))
        self._get_merges_info()
        logger.info("Generating commits general info for repo '{0}'".format(repo_name))
        self._get_commits_general_info()
        logger.info("Generating commits messages for repo '{0}'".format(repo_name))
        self._get_commits_messages()
        logger.info("Generating information about insertions and deletions for repo '{0}'".format(repo_name))
        self._get_number_of_insertions_and_deletions_for_all_commits()

        # Go back to the initial directory
        os.chdir(initial_dir)

def generate_raw_data_for_all_repos(repos_dir: str, output_dir: str) -> None:
    """
    Generates raw data files for all repositories stored in provided
    directory.

    :param repos_dir: directory where repos are stored
    :param output_dir: where to store the output raw files
    """

    # Get paths to all repos in given dir
    repos_paths = [
        f.path
        for f in os.scandir(repos_dir) if f.is_dir()
    ]

    for single_path in repos_paths:
        RawDataRetriever(
            repo_path=single_path, output_dir=output_dir
        ).generate_raw_data()
