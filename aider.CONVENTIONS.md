# Aider Coding Conventions

This document describes the coding conventions and patterns used by the AI assistant when making
changes to the codebase.

## Coding Standards

Running builds, installs, tests and runs should be done via  `scripts` directory. This ensures that
all projects have a consistent structure and can be easily maintained.

### Script Pattern

```bash
#!/bin/bash
set -e
export AWS_PROFILE=zindicomp
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
```

### Required Functions

With all of these functions if there are multiple components that could be built, tested, etc. there
could be multiple functions for each component.

These should have a suffix that describes what is.

For example, if there are multiple lambdas in a
project, there could be multiple build functions for each lambda.

There should also be a `all` suffix if there is more than one function for that step that could be
run, but only if their for that step.

If the is only one function for that step, then it should
not have the `all` suffix.

At the end of the step.

It should bring you back to the menu.

It should print the menu out again.
If nothing happens for 5s it should quit the script.

If run is passed a specific command to run.

It should not give the menu and it should directly
quit.

Pressing q should exit the script.

- help(): Display help text
- install_dependencies_<define>(): Install project dependencies
- run_<define>(): Execute code. There could be multiple run functions for different components.
- build_<define>): Build code if relevant it should specify what is building. If there are
  multiple things that could be built, there could be multiple build functions.
- test_<define>(): Execute test suite if available. This could be multiple test functions for
  different
  components. Also, flags could be used to run specific tests.
- package_<define>(): Create deployment package if needed. If there are multiple things that could
  be packaged, there could be multiple package functions.
- deploy_<define>(): Deploy infrastructure if required. This could be multiple deploy functions for
  different components.
- go_to_directory_<define>(): Open shell in project directory. This could be multiple
  go_to_directory
  functions for different components.
- lint_<define>(): Lint code if needed. If there are multiple things that could be linted, there
  could be multiple lint functions.
- all(): Run all steps in sequence
- quit(): Exit script

### Interactive Menu Format

```bash
PS3="Please select an option (1-X): "
options=("Option 1" "Option 2" "Option 3" "Quit")
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
