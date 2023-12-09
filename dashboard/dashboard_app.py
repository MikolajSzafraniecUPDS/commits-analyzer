import requests
import os
import importlib
import subprocess

from flask import Flask
from config import config

import logging.config
logging.config.fileConfig(os.path.join("config", "logging.conf"))
logger = logging.getLogger("consoleLogger")

app = Flask(__name__)


@app.route("/launch_dashboard")
def launch_dashboard() -> requests.Response:
    """
    Launch dashboard when the /run_dashboard endpoint is triggered.

    :return: HTTP response
    """

    # Reload config in case it was updated after deploying docker container
    importlib.reload(config)

    logger.info("Launching dashboard.")

    try:
        p = subprocess.Popen("python app.py", shell=True)
    except Exception as e:
        error_msg = str(e)
        res = app.response_class(
            response="Process of launching dashboard failed.\nError msg: '{0}'".format(
                error_msg
            ),
            status=500
        )
    else:
        res = app.response_class(
            response="Dashboard launched successfully.",
            status=200
        )

        logger.info("Dashboard launched successfully.")

    return res


if __name__ == "__main__":
    app.run(host="0.0.0.0")
