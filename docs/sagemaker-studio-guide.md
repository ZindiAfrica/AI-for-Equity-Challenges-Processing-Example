# Running with AWS SageMaker Studio (Recommended)

## Prerequisites
- Access to AWS SageMaker Studio (provided by competition organizers)
- Your team's S3 bucket permissions
- GitHub account with repository access
- Docker installed and configured (for local testing)
- AWS CLI configured with your credentials

## AWS CloudShell Setup

You can also run this pipeline directly from AWS CloudShell:

1. Open AWS CloudShell:
   - Go to AWS Console
   - Click the CloudShell icon in the top navigation bar
   - Wait for the shell environment to initialize

2. Clone and setup the repository:
   ```bash
   git clone git@github.com:ZindiAfrica/AI-for-Equity-Challenges-Processing-Example.git
   cd AI-for-Equity-Challenges-Processing-Example
   pip install --user -r requirements.txt
   ```

3. Configure git:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

4. Run the pipeline:
   ```bash
   python build_and_run_aws.py
   ```

5. Monitor progress:
   ```bash
   aws sagemaker list-processing-jobs
   aws sagemaker describe-processing-job --processing-job-name <job-name>
   ```

## SageMaker Studio Setup

1. Configure AWS credentials in SageMaker:
   - Open SageMaker Studio Terminal
   - Run AWS configuration:
   ```bash
   aws configure
   ```
   - Enter your:
     - AWS Access Key ID
     - AWS Secret Access Key
     - Default region (us-east-2)
     - Default output format (json)

2. Verify AWS configuration:
   ```bash
   aws sts get-caller-identity
   ```

3. Configure git in SageMaker:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

## Setup Instructions

1. Log into AWS Console and navigate to SageMaker Studio
2. Open SageMaker Studio and select your user profile
3. In the launcher, choose "Python 3 (PyTorch 2.0 Python 3.10 GPU Optimized)" kernel
4. Install required packages in a new cell:
```python
!curl -LsSf https://astral.sh/uv/install.sh | sh
!uv pip install -e ".[dev]"
!uv pip install -e ".[dev]" --system  # For system-wide installation
```

5. Clone this repository in a new cell:
```python
# If using SSH
!git clone git@github.com:ZindiAfrica/AI-for-Equity-Challenges-Processing-Example.git

# If using HTTPS with token
!git clone https://YOUR_TOKEN@github.com/ZindiAfrica/AI-for-Equity-Challenges-Processing-Example.git

%cd AI-for-Equity-Challenges-Processing-Example
```

## Running the Pipeline

### Method A: Direct Notebook Execution
Run notebooks in order:
```python
%run notebooks/outsmarting_data_prep.py
%run notebooks/outsmarting_train.py
%run notebooks/outsmarting_eval.py
%run notebooks/outsmarting_predict.py
```

### Method B: Using Step Functions
```python
import boto3
import json

# Create Step Functions client
sfn = boto3.client('stepfunctions')

# Define your pipeline
pipeline_definition = {
    "Comment": "ML Pipeline",
    "StartAt": "DataPrep",
    "States": {
        "DataPrep": {
            "Type": "Task",
            "Resource": "arn:aws:states:::sagemaker:createProcessingJob",
            "Parameters": {
                "ProcessingJobName": "data-prep-job",
                "ProcessingResources": {
                    "ClusterConfig": {
                        "InstanceCount": 1,
                        "InstanceType": "ml.m5.xlarge",
                        "VolumeSizeInGB": 30
                    }
                },
                "AppSpecification": {
                    "ImageUri": "YOUR_ECR_IMAGE",
                    "ContainerEntrypoint": ["python3", "outsmarting_data_prep.py"]
                }
            },
            "Next": "Training"
        },
        "Training": {
            "Type": "Task",
            "Resource": "arn:aws:states:::sagemaker:createTrainingJob",
            "End": true
        }
    }
}

# Start execution
response = sfn.start_execution(
    stateMachineArn='YOUR_STATE_MACHINE_ARN',
    input=json.dumps(pipeline_definition)
)
```

### Method C: Using AWS Batch
```python
import boto3

batch = boto3.client('batch')

# Submit job
response = batch.submit_job(
    jobName='ml-pipeline-job',
    jobQueue='YOUR_JOB_QUEUE',
    jobDefinition='YOUR_JOB_DEFINITION',
    containerOverrides={
        'command': ['python3', 'outsmarting_sagemaker_execute.py']
    }
)

# Monitor job status
job_id = response['jobId']
status = batch.describe_jobs(jobs=[job_id])['jobs'][0]['status']
print(f"Job Status: {status}")
```
