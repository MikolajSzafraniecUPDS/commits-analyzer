"""
Class responsible for creating .pdf reports for all repositories specified
in the analysis
"""

import os
import logging.config
import subprocess
import shutil

from typing import List
from config.config import *
from analysis.plots_and_tables_generator import PlotsAndTablesGenerator
from database.get_db_engine import get_db_engine

logging.config.fileConfig(os.path.join("config", "logging.conf"))
logger = logging.getLogger("consoleLogger")


class ReportsGenerator:

    def __init__(self, repos_names: List[str] = None):
        """
        Create an instance of the class

        :param repos_names: list containing names of the repos for which reports
            will be generated. If None - as default - all repos kept in the
            submodules dir will be taken
        """

        self.repos_names = self._get_repos_names() if repos_names is None else repos_names
        self.db_engine = get_db_engine(inside_compose_network=True)

    @staticmethod
    def _get_repos_names() -> List[str]:
        """
        Get base names of analyzed repositories

        :return: list of repos names as strings
        """

        res = [
            os.path.basename(path)
            for path in REPOS_TO_ANALYZE
        ]

        return res

    @staticmethod
    def _md_report_to_pdf(input_file_path: str, output_file_path: str) -> None:
        """
        Transform markdown file to pdf file

        :param input_file_path: path to the input file
        :param output_file_path: path to the output file
        """

        command = "mdpdf -o {0} {1}".format(
            output_file_path, input_file_path
        )
        subprocess.run(command, shell=True)

    @staticmethod
    def _copy_md_template(template_path: str, output_path: str) -> None:
        """
        Copy template of markdown report to target directory storing data
        for given repository

        :param template_path: path to report's template
        :param output_path: output path, please note that name of the
            output file can be different (not necessarily 'template.md').
        """

        # Get name of directory and create it if it doesn't exist yet
        dir_name = os.path.dirname(output_path)
        if not os.path.exists(dir_name):
            os.makedirs(output_path)

        shutil.copyfile(template_path, output_path)

    def generate_report_for_single_repo(self, repo_name: str) -> None:
        """
        Generate report for single repository.

        :param repo_name: name of the repository
        :param db_engine: database Engine object
        """

        template_path = os.path.join(ANALYSIS_RESULTS_DIR, "template.md")
        md_output_file_name = os.path.join(
            ANALYSIS_RESULTS_DIR, repo_name, "{0}_report.md".format(repo_name)
        )
        pdf_output_file_name = os.path.join(
            ANALYSIS_RESULTS_DIR, "{0}_report.pdf".format(repo_name)
        )

        plots_tables_generator = PlotsAndTablesGenerator(repo_name, db_engine=self.db_engine)
        plots_tables_generator.generate_all_plots_and_tables_for_given_report()

        logger.info("Copying markdown report template for repo {0}".format(repo_name))
        self._copy_md_template(template_path, md_output_file_name)
        logger.info("Generating pdf report template for repo {0}".format(repo_name))
        self._md_report_to_pdf(md_output_file_name, pdf_output_file_name)

    def generate_reports_for_all_repos(self) -> None:
        """
        Generates reports for all repositories specified in
        the class constructor
        """

        for repo_name in self.repos_names:
            logger.info("Generating report for repository '{0}'".format(repo_name))
            self.generate_report_for_single_repo(repo_name)
