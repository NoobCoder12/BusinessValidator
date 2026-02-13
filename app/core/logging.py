import logging
import sys


def setup_logging():
    """
    Logger setup.
    """
    # Format crated with class Formatter atributes 
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=logging.DEBUG,     # TODO: for production min. log level
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)   # Info where logs are displayed, sys.stdout == terminal, where app is displayed
        ]
    )


logger = logging.getLogger("business-validator")