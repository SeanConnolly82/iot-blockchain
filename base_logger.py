import logging

from colorlog import ColoredFormatter

def _get_console_handler():
    """ Set up a formatted console handler for the logger.

    Returns:
        console_handler: A stream handler object.
    """
    console_handler = logging.StreamHandler()
    console_formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    return console_handler


def _get_file_handler():
    """ Set up a formatted file handler for the logger.

    Returns:
        file_handler: A file handler object.
    """
    file_handler = logging.FileHandler('iot-log.log')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)
    return file_handler


def get_logger(name):
    """ Get a logger and add handlers.

    Returns:
        logger: A logging logger object.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name)
    logger.addHandler(_get_file_handler())
    logger.addHandler(_get_console_handler())
    logger.propagate = False
    return logger

