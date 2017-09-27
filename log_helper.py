import logging


def config_logging(file_name=None):
    logFormatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")
    logger = logging.getLogger()

    if file_name:
        fileHandler = logging.FileHandler(file_name)
        fileHandler.setFormatter(logFormatter)
        logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

    logger.setLevel(logging.INFO)
