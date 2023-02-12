import logging
import sys


def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    handler.setFormatter(formatter)

    # default logger
    default_logger = logging.getLogger()
    # remove default handler with formatter
    default_logger.handlers.clear()
    default_logger.setLevel(logging.INFO)
    default_logger.addHandler(handler)

