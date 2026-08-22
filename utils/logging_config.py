import logging
import logging.handlers
import os

# Get the directory of the current file, then go up one level to find the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOGS_DIR, "app.log")


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if already configured
    if logger.hasHandlers():
        return logger

    # Rotate logs every 2 days and keep only the latest log file
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=LOG_FILE_PATH,
        when="D",
        interval=2,
        backupCount=1,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
