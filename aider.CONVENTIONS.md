# Aider Coding Conventions

This document describes the coding conventions and patterns used by the AI assistant when making changes to the codebase.

## Standalone Terraform Module Conventions

### Variables and Defaults
When creating a new standalone Terraform module:

1. Update variables.tf with actual default values from tf/variables.tf:
```hcl
variable "region_comp" {
  description = "AWS region for competition resources"
  type = string
  default = "us-east-2"
}

variable "user_prefix" {
  description = "Prefix for IAM usernames" 
  type        = string
  default     = "comp-user-"
}

variable "zindi_tags" {
  type = map(string)
  default = {
    zindi        = "true"
    Environment  = "zindi-comp"
    managed_by   = "terraform"
    service      = "<service-name>"
  }
}
```

2. Replace user_names_map variable references:

Instead of:
```hcl
variable "user_names_map" {
  description = "Map of IAM usernames"
  type        = map(string)
}
```

Use IAM group lookup:
```hcl
data "aws_caller_identity" "aws_comp" {}

data "aws_iam_group" "comp_users" {
  group_name = "zindi-comp-group"
}

locals {
  user_names_map = { for user in data.aws_iam_group.comp_users.users : user.user_name => user.user_name }
}
```

3. Replace SageMaker role references:

Instead of:
```hcl
variable "sagemaker_team_roles" {
  type = map(object({
    name = string
    arn  = string
  }))
}
```

Use role lookup:
```hcl
data "aws_iam_role" "sagemaker_team_roles" {
  for_each = local.user_names_map
  name = "SageMakerRole-${each.key}"
}
```

### Provider Configuration

Update providers.tf with cloud configuration:

```hcl
terraform {
  required_version = "~> 1.10"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.82"
    }
  }
  cloud {
    organization = "zindi-aws-comp"
    workspaces {
      name = "<module-name>"
    }
  }
}

provider "aws" {
  region = var.region_comp
  
  default_tags {
    tags = var.zindi_tags
  }
}
```

## Lambda Function Management Scripts

### Script Pattern
```bash
#!/bin/bash
set -e
export AWS_PROFILE=zindicomp
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
```

### Required Functions
- usage(): Display help text
- build_lambda(): Build TypeScript code
- run_tests(): Execute test suite
- create_package(): Create deployment package
- deploy_terraform(): Deploy infrastructure

### Standard Options
1. build: Compile TypeScript
2. test: Run test suite
3. package: Create deployment zip
4. deploy: Run Terraform
5. all: Full build and deploy
6. Install Dependencies: npm install
7. Go to Directory: Open shell
8. Quit: Exit script

### Interactive Menu Format
```bash
PS3="Please select an option (1-8): "
options=("Build" "Test" "Package" "Deploy" "Build and Deploy" "Install Dependencies" "Go to Directory" "Quit")
select opt in "${options[@]}"
```

## TypeScript Project Structure

### Required Files
```
terraform-aws-{function-name}/
├── files/
│   └── {function-name}/
│       ├── src/           # TypeScript source
│       ├── dist/         # Compiled output
│       ├── tests/        # Test files
│       ├── package.json  # Dependencies
│       ├── tsconfig.json # TS config
│       ├── .eslintrc    # Linting rules
│       └── .prettierrc  # Format rules
```

### Configuration Standards
- ESLint: Use TypeScript parser and rules
- Prettier: Consistent formatting
- Jest: TypeScript testing
- tsconfig.json: Strict mode

## AWS Infrastructure Patterns

### Resource Naming
- Format: `zindi-{env}-{service}-{resource}`
- Use lowercase with hyphens
- Include environment name
- Add service identifier

### Required Tags
- Environment
- Service
- Team
- CostCenter
- ManagedBy

### Security Standards
- Least privilege IAM
- Resource encryption
- VPC isolation
- CloudWatch logging

## Version Control

### Commit Messages
Format: `type: description`
Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- refactor: Code change
- test: Test updates
- chore: Maintenance

### Branch Strategy
- feature/
- bugfix/
- release/
- hotfix/

## Testing Requirements
- Unit tests for functions
- Integration tests for AWS
- Infrastructure validation
- Security compliance checks
