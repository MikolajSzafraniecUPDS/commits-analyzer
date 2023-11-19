"""
Get database engine
"""

import os

import logging.config
from config.config import *
from sqlalchemy import create_engine, Engine

logging.config.fileConfig(os.path.join("config", "logging.conf"))
logger = logging.getLogger("consoleLogger")


def get_db_engine() -> Engine:
    """
    Get database Engine object

    :return: Engine object
    """

    connection_string = "postgresql://{username}:{password}@{host}:{port}/{db_name}".format(
        username=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        db_name=POSTGRES_DB
    )
    logger.info("Creating DB engine")
    engine = create_engine(connection_string)
    return engine
