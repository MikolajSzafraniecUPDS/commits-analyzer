import requests
import os
import importlib

from flask import Flask
from config import config

from analysis.report_generator import ReportsGenerator

import logging.config
logging.config.fileConfig(os.path.join("config", "logging.conf"))
logger = logging.getLogger("consoleLogger")

app = Flask(__name__)


@app.route("/run_analysis")
def run_analysis() -> requests.Response:
    """
    Run analysis process when the /run_analysis endpoint is triggered.

    :return: HTTP response
    """

    # Reload config in case it was updated after deploying docker container
    importlib.reload(config)

    logger.info("Launching analysis process.")

    try:
        logger.info("Generating .md and .pdf reports.")
        rg = ReportsGenerator()
        rg.generate_reports_for_all_repos()
    except Exception as e:
        error_msg = str(e)
        res = app.response_class(
            response="Analysis process failed.\nError msg: '{0}'".format(
                error_msg
            ),
            status=500
        )
    else:
        res = app.response_class(
            response="Analysis process finished successfully",
            status=200
        )

        logger.info("Reports generated successfully.")

    return res


if __name__ == "__main__":
    app.run(host="0.0.0.0")
