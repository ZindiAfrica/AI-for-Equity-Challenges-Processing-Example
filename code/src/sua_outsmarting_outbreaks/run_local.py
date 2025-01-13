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
DEFAULT_DATA_DIR = Path(__file__).parent.parent.parent / "data"
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent.parent / "output"

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

    # Convert relative paths to absolute from project root
    project_root = Path(__file__).parent.parent.parent.parent
    data_dir = (project_root / args.data_dir).resolve()
    output_dir = (project_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Log paths for debugging
        logger.info(f"Data directory: {data_dir}")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Current working directory: {Path.cwd()}")

        if args.stage in ("data-prep", "all"):
            logger.info("Running data preparation...")
            logger.debug(f"Input files in {args.data_dir}:")
            for f in Path(args.data_dir).glob('*.csv'):
                logger.debug(f"- {f.name}")
            
            preprocess_data(
                local_data_dir=args.data_dir,
                output_dir=str(output_dir)
            )

        if args.stage in ("train", "all"):
            logger.info("Running model training...")
            train_path = output_dir / "processed_train.csv"
            logger.info(f"Looking for training data at: {train_path}")
            
            if not train_path.exists():
                logger.error(f"Training data not found at {train_path}")
                logger.debug("Output directory contents:")
                for f in Path(args.output_dir).glob('*'):
                    logger.debug(f"- {f.name}")
                raise FileNotFoundError(f"Training data not found at {train_path}")
                
            train_df = pd.read_csv(train_path)
            logger.info(f"Loaded training data with shape: {train_df.shape}")
            
            X, y = prepare_features(train_df, "Total", ["ID", "Location"])
            logger.info(f"Prepared features X: {X.shape}, y: {y.shape}")
            
            train_model(features=X, target=y, data_dir=args.output_dir)

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
