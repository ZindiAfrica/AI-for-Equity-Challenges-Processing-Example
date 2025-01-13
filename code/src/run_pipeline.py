"""Script for running the ML pipeline locally or on AWS."""

import argparse
import logging
import sys
from pathlib import Path

from sua_outsmarting_outbreaks.data.data_prep import preprocess_data
from sua_outsmarting_outbreaks.models.train import train_model
from sua_outsmarting_outbreaks.models.evaluate import evaluate_model
from sua_outsmarting_outbreaks.predict.predict import generate_predictions
from sua_outsmarting_outbreaks.utils.logging_utils import setup_logger

# Configure logger
logger = setup_logger(__name__)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run ML pipeline stages")
    parser.add_argument(
        "--stage",
        choices=["prepare", "train", "evaluate", "predict", "all"],
        required=True,
        help="Pipeline stage to run",
    )
    parser.add_argument(
        "--local-data",
        type=str,
        help="Local directory containing input data files",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Local directory for output files",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )
    return parser.parse_args()

def main() -> None:
    """Execute pipeline stages."""
    args = parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        if args.stage == "prepare":
            logger.info("Running data preparation...")
            preprocess_data(
                local_data_dir=args.local_data,
                output_dir=args.output_dir
            )
        elif args.stage == "train":
            logger.info("Running model training...")
            train_model(data_dir=args.output_dir)
        elif args.stage == "evaluate":
            logger.info("Running model evaluation...")
            evaluate_model(data_dir=args.output_dir)
        elif args.stage == "predict":
            logger.info("Running predictions...")
            generate_predictions(data_dir=args.output_dir)
        elif args.stage == "all":
            logger.info("Running full pipeline...")
            
            # First prepare the data
            preprocess_data(
                local_data_dir=args.local_data,
                output_dir=args.output_dir
            )
            
            # Then train the model
            train_model(data_dir=args.output_dir)
            
            # Then evaluate
            evaluate_model(data_dir=args.output_dir)
            
            # Finally predict
            generate_predictions(data_dir=args.output_dir)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
