# SUA Outsmarting Outbreaks Challenge Example

This repository contains example code for running ML pipelines on AWS using SageMaker. You can run this example in two ways:

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
!git clone <repository-url>
%cd sua-outsmarting-outbreaks-example
```

6. Open and run the notebooks in order:
- `notebooks/outsmarting_data_prep.py`
- `notebooks/outsmarting_train.py`
- `notebooks/outsmarting_eval.py`
- `notebooks/outsmarting_predict.py`

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
