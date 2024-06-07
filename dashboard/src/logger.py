import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", logging.INFO)


def configure_logger(name) -> logging.Logger:
    logging.basicConfig(
        level = LOG_LEVEL,
        format="[%(asctime)s] - [%(name)s] - [%(levelname)s] - [%(message)s]",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(name)
    return logger