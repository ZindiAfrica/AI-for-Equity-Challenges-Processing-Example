"""Main pipeline module for orchestrating SageMaker processing jobs."""
import logging
from typing import List

import boto3
import sagemaker
from sagemaker.image_uris import retrieve as retrieve_image_uri
from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor

from sua_outsmarting_outbreaks.utils.aws_utils import (
    get_data_bucket_name,
    get_execution_role,
    get_script_processor_type,
    get_user_bucket_name,
    get_user_name,
)
from sua_outsmarting_outbreaks.utils.config import settings
from sua_outsmarting_outbreaks.utils.constants import (
    DATA_PREP_OUTPUT,
    DATA_PREP_SCRIPT,
    EVALUATION_OUTPUT,
    MAX_RUNTIME_SECONDS,
    MODEL_EVALUATION_SCRIPT,
    MODEL_PREDICTION_SCRIPT,
    MODEL_TRAINING_SCRIPT,
    PREDICTIONS_OUTPUT,
    TRAINING_OUTPUT,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize SageMaker session with explicit bucket
sagemaker_session = sagemaker.Session()

sts = boto3.client("sts")

username = get_user_name()
role = get_execution_role()
data_bucket_name = get_data_bucket_name()
user_bucket_name = get_user_bucket_name()

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
image_uri = retrieve_image_uri(framework=framework, region=region, version=version,
                               image_scope="inference")

print(f"Image URI: {image_uri}")

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

# Execute Data Preparation Script
print("Starting Data Preparation Job...")
try:
  data_prep_job = script_processor.run(
    code=data_prep_script,
    inputs=[ProcessingInput(source=input_prefix, destination="/opt/ml/processing/input")],
    outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                              destination=output_prefix + "data_prep/")],
  )
  data_prep_job.wait()
  print("Data Preparation Job completed successfully.")
except Exception as e:
  print(f"Data Preparation Job failed: {str(e)}")
  print("Please check CloudWatch logs for detailed error information.")
  # Get the job name to help locate logs
  if hasattr(data_prep_job, "job_name"):
    print(f"Job name: {data_prep_job.job_name}")
  raise

# Execute Model Training Script
print("Starting Model Training Job...")
training_job = script_processor.run(
  code=model_training_script,
  inputs=[
    ProcessingInput(
      source=output_prefix + "data_prep/processed_train.csv",
      destination="/opt/ml/processing/input",
    )
  ],
  outputs=[
    ProcessingOutput(source="/opt/ml/processing/output", destination=output_prefix + "training/")],
)
training_job.wait()
print("Model Training Job completed.")

# Execute Model Evaluation Script
print("Starting Model Evaluation Job...")
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
    )
  ],
)
evaluation_job.wait()
print("Model Evaluation Job completed.")

# Execute Model Prediction Script
print("Starting Model Prediction Job...")
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
    )
  ],
)
prediction_job.wait()
print("Model Prediction Job completed.")
