# Import necessary libraries
import os

import boto3
import sagemaker
from sagemaker.image_uris import retrieve as retrieve_image_uri
from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor

from sua_outsmarting_outbreaks.utils.aws_utils import get_execution_role, get_user_name

# Initialize SageMaker session with explicit bucket
sagemaker_session = sagemaker.Session()
sagemaker_session.default_bucket = lambda: "comp-user-5ow9bw-team-bucket"

# Get username for tagging
sts = boto3.client("sts")
username = sts.get_caller_identity()["Arn"].split("/")[-1]

role = get_execution_role()

# Define common tags
tags = [{"Key": "team", "Value": username}]

# Define the S3 bucket for input and output data
bucket_name = os.environ.get("SRC_BUCKET_NAME", "sua-outsmarting-outbreaks-challenge-comp")
out_bucket_name = os.environ.get("BUCKET_NAME", f"{workspace_name}-team-bucket")
input_prefix = f"s3://{bucket_name}/"
output_prefix = f"s3://{out_bucket_name}/output/"

# Define the scripts for each stage (local paths expected for `code` argument)
data_prep_script = "sua_outsmarting_outbreaks/data/data_prep.py"
model_training_script = "sua_outsmarting_outbreaks/models/train.py"
model_evaluation_script = "sua_outsmarting_outbreaks/models/evaluate.py"
model_prediction_script = "sua_outsmarting_outbreaks/predict/predict.py"

# Specify framework details
framework = "sklearn"
version = "0.23-1"  # Replace with desired version
region = "us-east-2"  # Replace with your AWS region

# Retrieve the image URI
image_uri = retrieve_image_uri(framework=framework, region=region, version=version, image_scope="inference")

print(f"Image URI: {image_uri}")

# Common arguments for all jobs
script_processor = ScriptProcessor(
    image_uri=image_uri,
    command=["python3"],
    role=role,
    instance_count=1,
    instance_type="ml.m5.2xlarge",  # $0.46/hr on-demand, $0.138/hr spot
    sagemaker_session=sagemaker_session,
    tags=tags,
)

# Execute Data Preparation Script
print("Starting Data Preparation Job...")
try:
    data_prep_job = script_processor.run(
        code=data_prep_script,
        inputs=[ProcessingInput(source=input_prefix, destination="/opt/ml/processing/input")],
        outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination=output_prefix + "data_prep/")],
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
    outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination=output_prefix + "training/")],
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
