"""
Get database engine
"""

import os

import logging.config
from config.config import *
from sqlalchemy import create_engine, Engine

logging.config.fileConfig(os.path.join("config", "logging.conf"))
logger = logging.getLogger("consoleLogger")


def get_db_engine(inside_compose_network: bool = False) -> Engine:
    """
    Get database Engine object

    :param inside_compose_network: bool indicating whether connection is established
        inside docker compose network or not
    :return: Engine object
    """

    if inside_compose_network:
        PG_HOST = POSTGRES_HOST_COMPOSE
    else:
        PG_HOST = POSTGRES_HOST

    connection_string = "postgresql://{username}:{password}@{host}:{port}/{db_name}".format(
        username=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=PG_HOST,
        port=POSTGRES_PORT,
        db_name=POSTGRES_DB
    )
    logger.info("Creating DB engine")
    engine = create_engine(connection_string)
    return engine
