# Using AWS Console and Local Development

## Prerequisites

1. AWS CLI configured with your credentials
2. Python 3.10+ installed locally
3. Required Python packages:
```bash
pip install pandas scikit-learn boto3 sagemaker
```

## Setup Instructions

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
