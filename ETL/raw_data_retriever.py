"""
Class that can be used to extract raw commit data from the
repository
"""

import os
import subprocess
import logging.config

from pathlib import Path
from typing import Dict

from config.config import OUTPUT_FILES, GENERAL_INFO_FORMAT, HEADERS

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
        Generate headers line for given file based using HEADERS
        dictionary.

        :param file_type: type of the file (one of keys from HEADERS dict)
        :return: headers line, separated with semicolon with '\n' at the end
        """

        res = ";".join(HEADERS.get(file_type)) + "\n"
        return res

    def _get_commit_hashes_no_merges(self) -> None:
        """
        Get a list of hashes of all commits except merges
        and store them in the .csv file
        """

        output_file = os.path.join(
            self.output_dir, OUTPUT_FILES.get("commits_hashes")
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
            self.output_dir, OUTPUT_FILES.get("merges_info")
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
            self.output_dir, OUTPUT_FILES.get("commits_info")
        )

        headers = self._generate_headers("commits_info")
        with open(output_file, 'w') as f:
            f.write(headers)

        command = "git log --no-merges --all --pretty=format:{0} >> {1}".format(
            GENERAL_INFO_FORMAT, output_file
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
            self.output_dir, OUTPUT_FILES.get("commits_messages")
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
    def _extract_number_of_insertions_and_deletions(commit_hash: str) -> Dict[str, int]:
        """
        Helper function to '_get_insertions_deletions_info'. It
        uses awk tool to extract information about number of insertions
        and deletions for given commit.

        :param commit_hash: hash of the commit for which we want to get information
            about
        :return: dictionary containing number of insertions and deletions for
            given commit
        """

        command = """
        git show --shortstat {0} | awk '{{
            # Keep track of the last line
            lastLine = $0
        }}
        END {{
            # Split the last line by space character
            split(lastLine, elements)
            # Check conditions and print accordingly
            if (length(elements) == 7) {{
                print elements[4] "," elements[6]
            }} else if (length(elements) == 5 && substr(elements[5], 1, 1) == "I") {{
                print elements[4] ",0"
            }} else if (length(elements) == 5 && substr(elements[5], 1, 1) == "D") {{
                print "0," elements[4]
            }} else {{
                print "0,0" # Return zeros separated by comma in all other cases
            }}
        }}'""".format(commit_hash)
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output = proc.stdout.read().decode().strip().split(",")
        res = {
            "insertions": int(output[0]),
            "deletions": int(output[1])
        }

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

        try:
            insertions_deletions_info = self._extract_number_of_insertions_and_deletions(
                commit_hash
            )
            insertions = insertions_deletions_info.get("insertions")
            deletions = insertions_deletions_info.get("deletions")
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
            OUTPUT_FILES.get("commits_hashes")
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
            self.output_dir, OUTPUT_FILES.get("insertions_deletions")
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
