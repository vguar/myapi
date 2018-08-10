import logging
import logging.config
from os import getenv


LOG_CONFIG_FILE = getenv('LOG_CONFIG_FILE', './logging.ini')

LOG = None


def get_logger():
    global LOG
    if LOG is None:
        logging.config.fileConfig(LOG_CONFIG_FILE)
        LOG = logging.getLogger('amazingresources')
    return LOG
