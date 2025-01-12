"""Logging utilities for the SUA Outsmarting Outbreaks Challenge."""

import logging
import sys
from pathlib import Path


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Path | None = None,
) -> logging.Logger:
    """Configure and return a logger with consistent formatting.

    Args:
        name: Name for the logger instance
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to write logs to file

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Starting process...")

    """
    logger = logging.getLogger(name)

    # Set log level
    level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(level)

    # Create formatters and handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

class MLPipelineError(Exception):
    """Base exception class for ML pipeline errors."""

    pass

class DataError(MLPipelineError):
    """Raised when there are issues with data loading or processing."""

    pass

class ModelError(MLPipelineError):
    """Raised when there are issues with model operations."""

    pass

class AWSError(MLPipelineError):
    """Raised when there are issues with AWS services."""

    pass
