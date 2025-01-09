# SUA Outsmarting Outbreaks Challenge Example

This repository contains example code for running ML pipelines on AWS using SageMaker. It demonstrates how to work with the infrastructure defined in the [ZindiAwsComp](https://github.com/ZindiAfrica/ZindiAwsComp) repository.

## Documentation

Choose your preferred method to run the pipeline:

1. [Using AWS SageMaker Studio](docs/sagemaker-studio-guide.md) (Recommended)
2. [Local Development with AWS Console](docs/local-development-guide.md)
3. [Troubleshooting Guide](docs/troubleshooting-guide.md)

## Repository Structure

```
.
├── notebooks/                     # Example Jupyter notebooks
│   ├── outsmarting_data_prep.py  # Data preprocessing script
│   ├── outsmarting_train.py      # Model training script
│   ├── outsmarting_eval.py       # Model evaluation script
│   └── outsmarting_predict.py    # Prediction generation script
├── docs/                         # Detailed documentation
├── Dockerfile                    # Container definition for SageMaker
├── build_and_push.sh            # Script to build and push Docker image
├── build_and_run_aws.py         # Script to execute pipeline on AWS
└── requirements.txt             # Python dependencies
```

## Getting Help

- Check the [documentation](https://github.com/ZindiAfrica/AI-for-Equity-Challenges-Getting-Started-with-AWS-Resources)
- Contact competition organizers
- Review AWS service quotas

## License

Proprietary - All rights reserved
