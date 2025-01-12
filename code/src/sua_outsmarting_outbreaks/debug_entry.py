import os
import time
from pathlib import Path

from dotenv import load_dotenv

from sua_outsmarting_outbreaks.utils.logging_utils import setup_logger

# Configure logger
logger = setup_logger(__name__)


def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        logger.warning("Warning: .env file not found, using system environment variables")


def print_settings():
    """Print environment settings excluding secrets"""
    logger.info("\nCurrent Settings:")
    logger.info("-" * 50)
    for key, value in sorted(os.environ.items()):
        # Skip AWS secret key and any other sensitive data
        if "SECRET" not in key.upper() and "PASSWORD" not in key.upper():
            logger.info(f"{key}={value}")
    logger.info("-" * 50)


if __name__ == "__main__":
    load_env()
    print_settings()
    logger.info("\nContainer is running in debug mode. Use Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nExiting debug mode...")
