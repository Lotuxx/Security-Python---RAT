import logging
from colorlog import ColoredFormatter


def setup_logger():
    logger = logging.getLogger("server")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate logs
    if logger.hasHandlers():
        return logger

    # -------- Console Handler (colored) -------- #
    console_handler = logging.StreamHandler()

    console_formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        }
    )

    console_handler.setFormatter(console_formatter)

    # ------- File Handler ------- #
    file_handler = logging.FileHandler("server.log")

    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler.setFormatter(file_formatter)

    # -------- Add handlers -------- #
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Global logger instance
logger = setup_logger()