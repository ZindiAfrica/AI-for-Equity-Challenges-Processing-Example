# Import necessary libraries
import boto3
import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from sagemaker import image_uris

# Initialize SageMaker session and role
sagemaker_session = sagemaker_session = sagemaker.Session(default_bucket="comp-user-5ow9bw-team-bucket")
role = sagemaker.get_execution_role()

# Define the S3 bucket for input and output data
bucket_name = 'sua-outsmarting-outbreaks-challenge-comp'
out_bucket_name = 'comp-user-5ow9bw-team-bucket'
input_prefix = f's3://{bucket_name}/'
output_prefix = f's3://{out_bucket_name}/output/'

# Define the scripts for each stage (local paths expected for `code` argument)
data_prep_script = "./outsmarting_data_prep.py"
model_training_script = "./outsmarting_train.py"
model_evaluation_script = "./outsmarting_eval.py"
model_prediction_script = "./outsmarting_predict.py"

from sagemaker.image_uris import retrieve

# Specify framework details
framework = "sklearn"
version = "0.23-1"  # Replace with desired version
region = "us-east-2"  # Replace with your AWS region

# Retrieve the image URI
image_uri = image_uris.retrieve(framework=framework,region=region, version=version, image_scope='inference')

print(f"Image URI: {image_uri}")

# Common arguments for all jobs
script_processor = ScriptProcessor(
    image_uri=image_uri,
    command=["python3"],
    role=role,
    instance_count=1,
    instance_type="ml.m5.large",
    sagemaker_session=sagemaker_session
)

# Execute Data Preparation Script
print("Starting Data Preparation Job...")
data_prep_job = script_processor.run(
    code=data_prep_script,
    inputs=[ProcessingInput(source=input_prefix, destination="/opt/ml/processing/input")],
    outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination=output_prefix + "data_prep/")]
)
data_prep_job.wait()
print("Data Preparation Job completed.")

# Execute Model Training Script
print("Starting Model Training Job...")
training_job = script_processor.run(
    code=model_training_script,
    inputs=[ProcessingInput(source=output_prefix + "data_prep/processed_train.csv", destination="/opt/ml/processing/input")],
    outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination=output_prefix + "training/")]
)
training_job.wait()
print("Model Training Job completed.")

# Execute Model Evaluation Script
print("Starting Model Evaluation Job...")
evaluation_job = script_processor.run(
    code=model_evaluation_script,
    inputs=[
        ProcessingInput(source=output_prefix + "data_prep/processed_test.csv", destination="/opt/ml/processing/input/test"),
        ProcessingInput(source=output_prefix + "training/random_forest_model.joblib", destination="/opt/ml/processing/input/model")
    ],
    outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination=output_prefix + "evaluation/")]
)
evaluation_job.wait()
print("Model Evaluation Job completed.")

# Execute Model Prediction Script
print("Starting Model Prediction Job...")
prediction_job = script_processor.run(
    code=model_prediction_script,
    inputs=[
        ProcessingInput(source=output_prefix + "data_prep/processed_test.csv", destination="/opt/ml/processing/input/test"),
        ProcessingInput(source=output_prefix + "training/random_forest_model.joblib", destination="/opt/ml/processing/input/model")
    ],
    outputs=[ProcessingOutput(source="/opt/ml/processing/output", destination=output_prefix + "predictions/")]
)
prediction_job.wait()
print("Model Prediction Job completed.")
