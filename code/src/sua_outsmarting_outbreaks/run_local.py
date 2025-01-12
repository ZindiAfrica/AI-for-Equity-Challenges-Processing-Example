"""Local execution script for running pipeline stages individually."""

import argparse
import logging
import sys
from pathlib import Path

from sua_outsmarting_outbreaks.data.data_prep import preprocess_data
from sua_outsmarting_outbreaks.models.train import train_model
from sua_outsmarting_outbreaks.models.evaluate import evaluate_model
from sua_outsmarting_outbreaks.predict.predict import generate_predictions
from sua_outsmarting_outbreaks.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run ML pipeline stages locally")
    parser.add_argument(
        "--stage",
        choices=["data-prep", "train", "evaluate", "predict", "all"],
        required=True,
        help="Pipeline stage to run",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )
    return parser.parse_args()

def main() -> None:
    """Execute pipeline stages locally."""
    args = parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        if args.stage in ("data-prep", "all"):
            logger.info("Running data preparation...")
            preprocess_data()

        if args.stage in ("train", "all"):
            logger.info("Running model training...")
            train_model()

        if args.stage in ("evaluate", "all"):
            logger.info("Running model evaluation...")
            evaluate_model()

        if args.stage in ("predict", "all"):
            logger.info("Running predictions...")
            generate_predictions()

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
