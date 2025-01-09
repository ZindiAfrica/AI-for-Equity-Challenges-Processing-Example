# SUA Outsmarting Outbreaks Challenge Example

This repository contains example code for running ML pipelines on AWS using SageMaker.

## Example CI/CD Pipeline

The `.github/workflows/ml-pipeline.yml` file shows how to set up automated deployments:

```yaml
name: ML Pipeline
on:
  push:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to run against'
        required: true
        default: 'staging'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-2

      - name: Start SageMaker Pipeline
        run: |
          aws sagemaker start-pipeline-execution \
            --pipeline-name ml-training-pipeline \
            --pipeline-execution-display-name github-action-${GITHUB_SHA}
```

## Authentication Setup

### 1. GitHub Authentication
Choose one of these methods:

#### Option A: SSH Keys (Recommended)
1. Generate an ED25519 SSH key:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. Start SSH agent and add your key:
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

3. Copy your public key:
```bash
cat ~/.ssh/id_ed25519.pub
```

4. Add the key to GitHub:
   - Go to GitHub Settings → SSH Keys
   - Click "New SSH Key"
   - Paste your public key

#### Option B: Personal Access Token
1. Generate a token:
   - Go to GitHub Settings → Developer Settings → Personal Access Tokens
   - Click "Generate New Token"
   - Select repo scope
   - Copy the generated token

2. Use the token with HTTPS:
```bash
git clone https://YOUR_TOKEN@github.com/ZindiAfrica/AI-for-Equity-Challenges-Processing-Example.git
```

### 2. AWS Authentication
1. Configure AWS CLI:
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Region: us-east-2
# Output format: json
```

2. Test AWS access:
```bash
aws sts get-caller-identity
```

## Getting Started

Clone this repository using your preferred authentication method:

```bash
# Using SSH
git clone git@github.com:ZindiAfrica/AI-for-Equity-Challenges-Processing-Example.git

# Using HTTPS with token
git clone https://YOUR_TOKEN@github.com/ZindiAfrica/AI-for-Equity-Challenges-Processing-Example.git

# Public read-only access
git clone https://github.com/ZindiAfrica/AI-for-Equity-Challenges-Processing-Example.git
```

## Running the Example

You can run this example in several ways:

## Option 1: Using AWS SageMaker Studio (Recommended)

### Prerequisites
- Access to AWS SageMaker Studio (provided by competition organizers)
- Your team's S3 bucket permissions

### Setup Instructions

1. Log into AWS Console and navigate to SageMaker Studio
2. Open SageMaker Studio and select your user profile
3. In the launcher, choose "Python 3 (PyTorch 2.0 Python 3.10 GPU Optimized)" kernel
4. Install required packages in a new cell:
```python
!pip install pandas scikit-learn boto3 sagemaker
```

5. Clone this repository in a new cell:
```python
# If using SSH
!git clone git@github.com:ZindiAfrica/AI-for-Equity-Challenges-Processing-Example.git

# If using HTTPS with token
!git clone https://YOUR_TOKEN@github.com/ZindiAfrica/AI-for-Equity-Challenges-Processing-Example.git

%cd AI-for-Equity-Challenges-Processing-Example
```

6. Run the Pipeline

#### Method A: Direct Notebook Execution
Run notebooks in order:
```python
%run notebooks/outsmarting_data_prep.py
%run notebooks/outsmarting_train.py
%run notebooks/outsmarting_eval.py
%run notebooks/outsmarting_predict.py
```

#### Method B: Using Step Functions
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

#### Method C: Using AWS Batch
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

## Option 2: Using AWS Console and Local Development

### Prerequisites

1. AWS CLI configured with your credentials
2. Python 3.10+ installed locally
3. Required Python packages:
```bash
pip install pandas scikit-learn boto3 sagemaker
```

### Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd sua-outsmarting-outbreaks-example
```

2. Configure AWS credentials in your environment:
```bash
export AWS_PROFILE=your-profile-name
```

3. Run the pipeline:
```python
python build_and_run_aws.py
```

## Repository Structure

```
.
├── notebooks/             # ML pipeline scripts
│   ├── outsmarting_data_prep.py    # Data preparation
│   ├── outsmarting_train.py        # Model training  
│   ├── outsmarting_eval.py         # Model evaluation
│   └── outsmarting_predict.py      # Prediction generation
└── build_and_run_aws.py   # Script to execute pipeline on SageMaker
```

## Output Locations

Results are saved to your team's S3 bucket:
- Processed data: `s3://<team-bucket>/output/data_prep/`
- Trained model: `s3://<team-bucket>/output/training/`
- Evaluation results: `s3://<team-bucket>/output/evaluation/`
- Final predictions: `s3://<team-bucket>/output/predictions/`

## Resource Configuration

The pipeline uses:
- GPU instance: ml.g4dn.8xlarge
- 100GB storage volume
- Maximum runtime: 24 hours

## Monitoring

Monitor job progress in:
1. SageMaker Studio interface
2. SageMaker console -> Processing jobs
3. CloudWatch logs

## Troubleshooting

Common issues:

1. Package installation fails
   - Try restarting the kernel
   - Check internet connectivity
   - Verify pip is up to date: `pip install --upgrade pip`

2. Permission errors
   - Verify you're using the correct team credentials
   - Check S3 bucket permissions
   - Ensure SageMaker execution role has required permissions

3. Resource limits
   - Check if you've hit the team's GPU instance quota
   - Monitor cost usage in AWS Cost Explorer
   - Contact competition organizers if needed

## Security Notes

- All resources are tagged with your team name
- Access is restricted to your team's resources
- Data is encrypted in transit and at rest
- Credentials are managed through AWS IAM
