"""Local execution script for running pipeline stages individually."""

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

from sua_outsmarting_outbreaks.data.data_prep import preprocess_data
from sua_outsmarting_outbreaks.models.train import prepare_features
from sua_outsmarting_outbreaks.models.evaluate import evaluate_model
from sua_outsmarting_outbreaks.models.train import train_model
from sua_outsmarting_outbreaks.predict.predict import generate_predictions
from sua_outsmarting_outbreaks.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

# Default paths
DEFAULT_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / "output"

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
        "--data-dir",
        type=str,
        default=str(DEFAULT_DATA_DIR),
        help="Directory containing input data files",
    )
    parser.add_argument(
        "--output-dir", 
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for output files",
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

    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        if args.stage in ("data-prep", "all"):
            logger.info("Running data preparation...")
            preprocess_data(
                local_data_dir=args.data_dir,
                output_dir=str(output_dir)
            )

        if args.stage in ("train", "all"):
            logger.info("Running model training...")
            train_df = pd.read_csv(Path(args.data_dir) / "processed_train.csv")
            X, y = prepare_features(train_df, "Total", ["ID", "Location"])
            train_model(features=X, target=y, data_dir=str(output_dir))

        if args.stage in ("evaluate", "all"):
            logger.info("Running model evaluation...")
            evaluate_model(data_dir=str(output_dir))

        if args.stage in ("predict", "all"):
            logger.info("Running predictions...")
            generate_predictions(data_dir=str(output_dir))

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
