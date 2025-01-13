"""Command line interface for running the ML pipeline locally or on AWS."""

import click
from pathlib import Path

from sua_outsmarting_outbreaks.data.data_prep import preprocess_data
from sua_outsmarting_outbreaks.models.train import train_model
from sua_outsmarting_outbreaks.models.evaluate import evaluate_model
from sua_outsmarting_outbreaks.predict.predict import generate_predictions
from sua_outsmarting_outbreaks.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

@click.group()
def cli():
    """CLI for running the ML pipeline locally or on AWS."""
    pass

@cli.command()
@click.option('--local-data', type=click.Path(), help='Local directory for input data')
@click.option('--output-dir', type=click.Path(), help='Local directory for output')
def prepare(local_data, output_dir):
    """Run data preparation step."""
    logger.info(f"Running data preparation with local_data={local_data}, output_dir={output_dir}")
    preprocess_data(local_data_dir=local_data, output_dir=output_dir)

@cli.command() 
@click.option('--input-dir', type=click.Path(), help='Directory with processed training data')
def train(input_dir):
    """Run model training step."""
    logger.info(f"Running model training with input_dir={input_dir}")
    train_model(data_dir=input_dir)

@cli.command()
@click.option('--input-dir', type=click.Path(), help='Directory with test data and model')
def evaluate(input_dir):
    """Run model evaluation step."""
    logger.info(f"Running model evaluation with input_dir={input_dir}")
    evaluate_model(data_dir=input_dir)

@cli.command()
@click.option('--input-dir', type=click.Path(), help='Directory with test data and model')
def predict(input_dir):
    """Generate predictions."""
    logger.info(f"Running prediction with input_dir={input_dir}")
    generate_predictions(data_dir=input_dir)

if __name__ == '__main__':
    cli()
