import logging
from logging.handlers import RotatingFileHandler

# Configure logging
def setup_logging(log_level=logging.DEBUG):
    """
    Set up logging with a configurable log level.
    
    Args:
        log_level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
    """
    # Create a logger
    logger = logging.getLogger("application_logger")
    logger.setLevel(log_level)

    # Create a rotating file handler (logs rotate after 1 MB, keep 5 backups)
    file_handler = RotatingFileHandler("app.log", maxBytes=1_000_000, backupCount=5)
    file_handler.setLevel(log_level)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Define a log format
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Example: Set the desired log level here (or pass it dynamically when calling setup_logging)
LOG_LEVEL = logging.DEBUG

# logging.DEBUG: Detailed information, typically for diagnosing problems.
# logging.INFO: General application events (default for most applications).
# logging.WARNING: An indication of something unexpected or potentially problematic.
# logging.ERROR: A more serious problem.
# logging.CRITICAL: A critical error, potentially causing the application to stop.

# Initialize the logger with the desired log level
logger = setup_logging(LOG_LEVEL)


