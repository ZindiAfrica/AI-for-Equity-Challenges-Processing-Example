# SUA Outsmarting Outbreaks Challenge Example

This repository contains example code for running ML pipelines on AWS using SageMaker. It demonstrates how to work with the infrastructure defined in the [ZindiAwsComp](https://github.com/ZindiAfrica/ZindiAwsComp) repository.

## Quick Start

1. Clone the repository and install dependencies:
```bash
git clone git@github.com:ZindiAfrica/AI-for-Equity-Challenges-Processing-Example.git
cd sua-outsmarting-outbreaks
./run.sh
```

2. Select your preferred execution method:
- Run locally: `./run.sh run-local`
- Run on AWS: `./run.sh run-aws`

## Documentation

For detailed documentation, please see the files in the docs folder.

### Running Options

1. [Using AWS SageMaker Studio](docs/sagemaker-studio-guide.md) (Recommended)
2. [Local Development](docs/local-development-guide.md)
3. [Docker Development](docs/docker-development-guide.md)
4. [Troubleshooting Guide](docs/troubleshooting-guide.md)

### Infrastructure Details
- [Project Structure](./docs/structure.md)
- [Module Dependencies](./docs/dependencies.md)
- [Billing & Cost Management](./docs/billing.md)

## Repository Structure

```
.
├── code/
│   ├── src/                      # Main source code
│   │   ├── sua_outsmarting_outbreaks/
│   │   │   ├── data/            # Data processing modules
│   │   │   ├── models/          # ML model modules
│   │   │   ├── predict/         # Prediction modules
│   │   │   └── utils/           # Utility functions
│   │   ├── tests/               # Test suite
│   │   └── pyproject.toml       # Dependencies and build config
│   ├── data/                    # Data directory
│   └── Dockerfile               # Container definition
├── docs/                        # Documentation
└── run.sh                      # Main execution script
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

### Core Dependencies

```mermaid
```

### Module Coupling Analysis

#### Tightly Coupled Modules

## Project Structure

### Documentation
- [docs/](./docs/) - User and administrator documentation


### Scripts
- [scripts/](./scripts/) - Management and utility scripts

## License

Proprietary - All rights reserved
