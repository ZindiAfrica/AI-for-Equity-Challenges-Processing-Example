# Aider Coding Conventions

This document describes the coding conventions and patterns used by the AI assistant when making changes to the codebase.

## Coding Standards

Running builds, installs, tests and runs should be done via  `scripts` directory. This ensures that all projects have a consistent structure and can be easily maintained.

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
