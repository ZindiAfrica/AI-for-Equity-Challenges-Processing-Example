"""Main pipeline module for orchestrating SageMaker processing jobs.

This module handles the end-to-end ML pipeline execution on AWS SageMaker, including:
- Data preparation
- Model training
- Model evaluation
- Prediction generation

The pipeline uses SageMaker Processing jobs to run each stage in a containerized
environment with specified compute resources.

Example:
    >>> from sua_outsmarting_outbreaks.pipeline import run_pipeline
    >>> run_pipeline()

"""

import logging

import boto3
import sagemaker
from sagemaker.image_uris import retrieve as retrieve_image_uri
from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor

from sua_outsmarting_outbreaks.utils.aws_utils import (
    get_data_bucket_name,
    get_execution_role,
    get_user_bucket_name,
    get_user_name,
)
from sua_outsmarting_outbreaks.utils.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def initialize_aws_resources() -> tuple[sagemaker.Session, str, str, str, str]:
    """Initialize AWS resources and sessions.

    Returns:
        tuple containing:
            sagemaker.Session: Initialized SageMaker session
            str: Username for resource tagging
            str: IAM role ARN for execution
            str: Data bucket name
            str: User bucket name

    """
    sagemaker_session = sagemaker.Session()
    username = get_user_name()
    role = get_execution_role()
    data_bucket_name = get_data_bucket_name()
    user_bucket_name = get_user_bucket_name()

    return sagemaker_session, username, role, data_bucket_name, user_bucket_name


# Initialize AWS resources
sagemaker_session, username, role, data_bucket_name, user_bucket_name = initialize_aws_resources()

# Define common tags
tags = [{"Key": "team", "Value": username}]

input_prefix = f"s3://{data_bucket_name}/"
output_prefix = f"s3://{user_bucket_name}/output/"

sagemaker_session.default_bucket = lambda: data_bucket_name

# Define the scripts for each stage (local paths expected for `code` argument)
data_prep_script = "sua_outsmarting_outbreaks/data/data_prep.py"
model_training_script = "sua_outsmarting_outbreaks/models/train.py"
model_evaluation_script = "sua_outsmarting_outbreaks/models/evaluate.py"
model_prediction_script = "sua_outsmarting_outbreaks/predict/predict.py"

# Get framework details from settings
framework = settings.model.framework
version = settings.model.framework_version
region = settings.aws.region

# Retrieve the image URI
image_uri = retrieve_image_uri(framework=framework, region=region, version=version, image_scope="inference")

logger.info(f"Image URI: {image_uri}")

# Common arguments for all jobs
script_processor = ScriptProcessor(
    image_uri=image_uri,
    command=["python3"],
    role=role,
    instance_count=settings.sagemaker.instance_count,
    instance_type=settings.sagemaker.instance_type,
    sagemaker_session=sagemaker_session,
    tags=tags,
)


def run_data_preparation(
    script_processor: ScriptProcessor,
    input_prefix: str,
    output_prefix: str,
    script_path: str,
) -> None:
    """Execute the data preparation stage of the pipeline.

    Args:
        script_processor: Configured SageMaker ScriptProcessor
        input_prefix: S3 prefix for input data
        output_prefix: S3 prefix for output data
        script_path: Path to data preparation script

    Raises:
        Exception: If the processing job fails

    """
    logger.info("Starting Data Preparation Job...")
    try:
        data_prep_job = script_processor.run(
            code=script_path,
            inputs=[ProcessingInput(source=input_prefix, destination="/opt/ml/processing/input")],
            outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination=output_prefix + "data_prep/")],
        )
        data_prep_job.wait()
        logger.info("Data Preparation Job completed successfully.")
    except Exception as e:
        logger.error(f"Data Preparation Job failed: {e!s}")
        logger.error("Please check CloudWatch logs for detailed error information.")
        if hasattr(data_prep_job, "job_name"):
            logger.error(f"Job name: {data_prep_job.job_name}")
        raise


# Execute Data Preparation Script
run_data_preparation(script_processor, input_prefix, output_prefix, data_prep_script)

# Execute Model Training Script
logger.info("Starting Model Training Job...")
training_job = script_processor.run(
    code=model_training_script,
    inputs=[
        ProcessingInput(
            source=output_prefix + "data_prep/processed_train.csv",
            destination="/opt/ml/processing/input",
        ),
    ],
    outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination=output_prefix + "training/")],
)
training_job.wait()
logger.info("Model Training Job completed.")

# Execute Model Evaluation Script
logger.info("Starting Model Evaluation Job...")
evaluation_job = script_processor.run(
    code=model_evaluation_script,
    inputs=[
        ProcessingInput(
            source=output_prefix + "data_prep/processed_test.csv",
            destination="/opt/ml/processing/input/test",
        ),
        ProcessingInput(
            source=output_prefix + "training/random_forest_model.joblib",
            destination="/opt/ml/processing/input/model",
        ),
    ],
    outputs=[
        ProcessingOutput(
            source="/opt/ml/processing/output",
            destination=output_prefix + "evaluation/",
        ),
    ],
)
evaluation_job.wait()
logger.info("Model Evaluation Job completed.")

# Execute Model Prediction Script
logger.info("Starting Model Prediction Job...")
prediction_job = script_processor.run(
    code=model_prediction_script,
    inputs=[
        ProcessingInput(
            source=output_prefix + "data_prep/processed_test.csv",
            destination="/opt/ml/processing/input/test",
        ),
        ProcessingInput(
            source=output_prefix + "training/random_forest_model.joblib",
            destination="/opt/ml/processing/input/model",
        ),
    ],
    outputs=[
        ProcessingOutput(
            source="/opt/ml/processing/output",
            destination=output_prefix + "predictions/",
        ),
    ],
)
prediction_job.wait()
logger.info("Model Prediction Job completed.")
