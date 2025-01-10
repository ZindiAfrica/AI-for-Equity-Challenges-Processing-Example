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
│   ├── sagemaker-studio-guide.md # AWS SageMaker Studio setup and usage
│   ├── local-development-guide.md # Local development instructions
│   └── troubleshooting-guide.md  # Common issues and solutions
├── Dockerfile                    # Container definition for SageMaker
├── build_and_run_aws.py         # Script to build Docker image and execute pipeline on AWS
└── requirements.txt             # Python dependencies
```

## GitHub Authentication Setup

### Generate SSH Key (Recommended)
1. Generate a new SSH key:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. Add to GitHub:
- Copy your public key:
```bash
cat ~/.ssh/id_ed25519.pub
```
- Go to GitHub → Settings → SSH Keys → New SSH Key
- Paste your public key and save

3. Add to SageMaker:
- Open SageMaker Studio
- Click File → New → Terminal
- Create SSH directory:
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
```
- Copy your private key:
```bash
vim ~/.ssh/id_ed25519  # Paste your private key here
chmod 600 ~/.ssh/id_ed25519
```

### Generate GitHub Token (Alternative)
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with 'repo' scope
3. Copy token and add to SageMaker:
```bash
git config --global credential.helper store
echo "https://YOUR_USERNAME:YOUR_TOKEN@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials
```

## Getting Help

- Check the [documentation](https://github.com/ZindiAfrica/AI-for-Equity-Challenges-Getting-Started-with-AWS-Resources)
- Contact competition organizers
- Review AWS service quotas

## License

Proprietary - All rights reserved
