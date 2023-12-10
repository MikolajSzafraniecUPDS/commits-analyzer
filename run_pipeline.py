"""
Run whole ETL process, starting from cloning repositories as submodules,
through retrieving commits data, loading preprocessed and aggregated
data to the DB to generate analysis and deploying a dashboard.
"""

import os
import requests
import webbrowser

from config import config
from threading import Timer
import logging.config

logging.config.fileConfig(os.path.join("config", "logging.conf"))
logger = logging.getLogger("consoleLogger")


def _config_to_str():
    """
    Convert configuration to string in order to pass it to logger.
    """

    output_str = ""
    for single_setting in dir(config):
        if not single_setting.startswith("__"):
            setting_val = "{0}: {1}".format(
                single_setting,
                getattr(config, single_setting)
            ) + "\n"
            output_str += setting_val

    return output_str


def _run_etl() -> requests.Response:
    """
    Run ETL process triggering Flask endpoint running in the ETL
    container.

    :return: ETL module response
    """
    etl_port = os.environ.get("ETL_APP_FLASK_PORT", "5000")
    r = requests.get(
        "http://127.0.0.1:{0}/run_etl".format(etl_port),
        timeout=1000
    )
    return r


def _run_analysis() -> requests.Response:
    """
    Run analysis process triggering Flask endpoint running in the analysis
    container.

    :return: analysis module response
    """
    analysis_port = os.environ.get("ANALYSIS_APP_FLASK_PORT", "5001")
    r = requests.get(
        "http://127.0.0.1:{0}/run_analysis".format(analysis_port),
        timeout=1000
    )
    return r


def _launch_dashboard() -> requests.Response:
    """
    Launch dashboard triggering Flash endpoint running in the dashboard
    container.

    :return: dashboard module response
    """
    dashboard_port = os.environ.get("DASH_APP_FLASH_PORT", "5002")
    r = requests.get(
        "http://127.0.0.1:{0}/launch_dashboard".format(dashboard_port),
        timeout=1000
    )
    return r


# Open dashboard in a Browser
def _open_browser():
    """
    Open browser automatically when launching an app.
    """
    dash_port = os.environ.get("DASH_PORT", '8050')
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new("http://localhost:{}".format(dash_port))


if __name__ == "__main__":

    logger.info("Launching commits-analyzer pipeline.")

    config_str = _config_to_str()
    logger.info("\nConfiguration:\n{0}".format(config_str))

    etl_reponse = _run_etl()

    if not etl_reponse.ok:
        raise requests.RequestException(
            "ETL process failed, error code: {0}, message: {1}".format(
                etl_reponse.status_code, etl_reponse.content.decode()
            )
        )
    else:
        logger.info("ETL process finished, response code: {0}, response message: {1}".format(
            etl_reponse.status_code, etl_reponse.content.decode())
        )

    analysis_response = _run_analysis()

    if not analysis_response.ok:
        raise requests.RequestException(
            "Analysis process failed, error code: {0}, message: {1}".format(
                analysis_response.status_code, analysis_response.content.decode()
            )
        )
    else:
        logger.info("Analysis process finished, response code: {0}, response message: {1}".format(
            analysis_response.status_code, analysis_response.content.decode())
        )

    dashboard_response = _launch_dashboard()

    if not dashboard_response.ok:
        raise requests.RequestException(
            "Process of launching dashboard failed, error code: {0}, message: {1}".format(
                dashboard_response.status_code, dashboard_response.content.decode()
            )
        )
    else:
        logger.info("Dashboard launched successfully, response code: {0}, response message: {1}".format(
            dashboard_response.status_code, dashboard_response.content.decode())
        )
        dash_port = os.environ.get("DASH_PORT", '8050')
        logger.info("Hosting dashboard at localhost, port: {0}".format(
            dash_port
        ))

        if config.LAUNCH_BROWSER:
            Timer(1, _open_browser).start()
