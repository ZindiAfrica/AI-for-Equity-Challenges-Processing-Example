#!/bin/bash
set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export APP_NAME="sua-outsmarting-outbreaks"
export APP_DIR="$SCRIPT_DIR/code/src"

# Load .env file if it exists
if [ -f "$APP_DIR/.env" ]; then
    echo "Loading environment variables from .env file..."
    set -a
    source "$APP_DIR/.env"
    set +a
else
    echo "No .env file found at $APP_DIR/.env"
    # Set default AWS profile if not set in environment
    [ -z "$AWS_PROFILE" ] && export AWS_PROFILE=zindicomp
fi

# Required functions with component suffixes
install_dependencies_python() {
    echo "Installing Python dependencies..."
    cd "$APP_DIR"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    pip install pytest pytest-cov
    pre-commit install
    echo "Dependencies installed successfully"
}

build_docker() {
    echo "Building Docker image..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python build_and_run_aws.py --build-only
}

test_python() {
    echo "Running Python tests..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python -m pytest
}

lint_python() {
    echo "Running Python linter..."
    cd "$APP_DIR"
    source .venv/bin/activate
    ruff check --fix .
    ruff format --check .
}

format_python() {
    echo "Formatting Python code..."
    cd "$APP_DIR"
    source .venv/bin/activate
    ruff format .
    ruff check --fix .
}

deploy_sagemaker() {
    echo "Deploying to AWS SageMaker..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python build_and_run_aws.py --deploy-only
}

go_to_directory_src() {
    cd "$APP_DIR"
    exec $SHELL
}

download_data() {
    echo "Downloading training data..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python download_data.py "$@"
}

run_prepare_local() {
    echo "Running data preparation step locally..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python -m sua_outsmarting_outbreaks.run_local --stage data-prep "$@"
}

run_train_local() {
    echo "Running model training step locally..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python -m sua_outsmarting_outbreaks.run_local --stage train "$@"
}

run_evaluate_local() {
    echo "Running model evaluation step locally..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python -m sua_outsmarting_outbreaks.run_local --stage evaluate "$@"
}

run_predict_local() {
    echo "Running prediction step locally..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python -m sua_outsmarting_outbreaks.run_local --stage predict "$@"
}

run_pipeline_local() {
    echo "Running full pipeline locally..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python -m sua_outsmarting_outbreaks.run_local --stage all "$@"
}

run_prepare_aws() {
    echo "Running data preparation step on AWS..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python pipeline.py --stage prepare "$@"
}

run_train_aws() {
    echo "Running model training step on AWS..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python pipeline.py --stage train "$@"
}

run_evaluate_aws() {
    echo "Running model evaluation step on AWS..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python pipeline.py --stage evaluate "$@"
}

run_predict_aws() {
    echo "Running prediction step on AWS..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python pipeline.py --stage predict "$@"
}

run_pipeline_aws() {
    echo "Running full pipeline on AWS..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python pipeline.py --stage all "$@"
}

all() {
    install_dependencies_python
    build_docker
    test_python
    package_docker
    deploy_sagemaker
    run_pipeline
}

quit() {
    exit 0
}

help() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  help                      - Display this help message"
    echo ""
    echo "Installation:"
    echo "  install                   - Install all dependencies"
    echo "  install-python           - Install Python dependencies only"
    echo ""
    echo "Building:"
    echo "  build                    - Build all components"
    echo "  build-docker            - Build Docker image only"
    echo ""
    echo "Testing:"
    echo "  test                     - Run all tests"
    echo "  test-python             - Run Python tests only"
    echo ""
    echo "Code Quality:"
    echo "  lint                     - Run Python linter"
    echo "  format                   - Format Python code"
    echo ""
    echo "Packaging:"
    echo "  package                  - Package all components"
    echo "  package-docker          - Package Docker image only"
    echo ""
    echo "Deployment:"
    echo "  deploy                   - Deploy all components"
    echo "  deploy-sagemaker        - Deploy to SageMaker only"
    echo ""
    echo "Execution:"
    echo "  run-local [options]     - Run the ML pipeline locally"
    echo "  run-aws [options]       - Run the ML pipeline on AWS"
    echo "  all                      - Run all steps in sequence"
    echo ""
    echo "Development:"
    echo "  shell                    - Open shell in source directory"
    echo ""
    echo "Options:"
    echo "  --debug                  - Run in debug mode"
    echo ""
    echo "Examples:"
    echo "  $0 install-python       # Install Python dependencies"
    echo "  $0 build-docker        # Build Docker image"
    echo "  $0 run                 # Run pipeline"
    echo "  $0 run --debug         # Run in debug mode"
    echo "  $0                     # Interactive mode"
}

# Function to display menu
show_menu() {
    PS3=$'\nPlease select an option (1-15) or "q" to quit: '
    REPLY=""

    # Set timeout of 5 seconds
    TMOUT=5

    # Trap timeout and exit
    trap 'echo -e "\nTimeout after 5 seconds of inactivity. Exiting..."; exit 0' ALRM
    options=(
        "Help"
        "Download Data"
        "Install Python Dependencies"
        "Build Docker Image"
        "Run Python Tests"
        "Lint Python Code"
        "Format Python Code"
        "Deploy to SageMaker"
        "Run Data Preparation (Local)"
        "Run Model Training (Local)"
        "Run Model Evaluation (Local)"
        "Run Predictions (Local)"
        "Run Full Pipeline (Local)"
        "Run Data Preparation (AWS)"
        "Run Model Training (AWS)"
        "Run Model Evaluation (AWS)"
        "Run Predictions (AWS)"
        "Run Full Pipeline (AWS)"
        "Run All Steps"
        "Go to Source Directory"
        "Quit"
    )
    while true; do
        select opt in "${options[@]}"
        do
            # Reset timeout for next iteration
            TMOUT=5

            # Handle direct q input
            if [[ "$REPLY" =~ ^[qQ]$ ]]; then
                exit 0
            fi

            case $opt in
            "Help")
                help
                ;;
            "Install Python Dependencies")
                install_dependencies_python
                show_menu
                ;;
            "Build Docker Image")
                build_docker
                show_menu
                ;;
            "Run Python Tests")
                test_python
                show_menu
                ;;
            "Lint Python Code")
                lint_python
                show_menu
                ;;
            "Format Python Code")
                format_python
                show_menu
                ;;
            "Deploy to SageMaker")
                deploy_sagemaker
                show_menu
                ;;
            "Download Data")
                download_data "$@"
                show_menu
                ;;
            "Run Data Preparation (Local)")
                run_prepare_local
                show_menu
                ;;
            "Run Model Training (Local)")
                run_train_local
                show_menu
                ;;
            "Run Model Evaluation (Local)")
                run_evaluate_local
                show_menu
                ;;
            "Run Predictions (Local)")
                run_predict_local
                show_menu
                ;;
            "Run Full Pipeline (Local)")
                run_pipeline_local
                show_menu
                ;;
            "Run Data Preparation (AWS)")
                run_prepare_aws
                show_menu
                ;;
            "Run Model Training (AWS)")
                run_train_aws
                show_menu
                ;;
            "Run Model Evaluation (AWS)")
                run_evaluate_aws
                show_menu
                ;;
            "Run Predictions (AWS)")
                run_predict_aws
                show_menu
                ;;
            "Run Full Pipeline (AWS)")
                run_pipeline_aws
                show_menu
                ;;
            "Run All Steps")
                all
                show_menu
                ;;
            "Go to Source Directory")
                go_to_directory_src
                show_menu
                ;;
            "Quit"|"q"|"Q")
                exit 0
                ;;
            *)
                echo "Invalid option $REPLY"
                break
                ;;
        esac
        break
    done
done
}

# Main execution
if [ $# -eq 0 ]; then
    show_menu
else
    # Direct command execution - no menu return
    case "$1" in
        "help")
            help
            ;;
        "install")
            install_dependencies_all
            ;;
        "install-python")
            install_dependencies_python
            ;;
        "build")
            build_all
            ;;
        "build-docker")
            build_docker
            ;;
        "test")
            test_all
            ;;
        "test-python")
            test_python
            ;;
        "lint")
            lint_python
            ;;
        "format")
            format_python
            ;;
        "deploy")
            deploy_all
            ;;
        "deploy-sagemaker")
            deploy_sagemaker
            ;;
        "run-evaluate-local")
            shift
            run_evaluate_local "$@"
            ;;
        "run-evaluate-aws")
            shift
            run_evaluate_aws "$@"
            ;;
        "download")
            shift
            download_data "$@"
            ;;
        "run-prepare-local")
            shift
            run_prepare_local "$@"
            ;;
        "run-prepare-aws")
            shift
            run_prepare_aws "$@"
            ;;
        "run-train-local")
            shift
            run_train_local "$@"
            ;;
        "run-train-aws")
            shift
            run_train_aws "$@"
            ;;
        "run-predict-local")
            shift
            run_predict_local "$@"
            ;;
        "run-predict-aws")
            shift
            run_predict_aws "$@"
            ;;
        "run-local")
            shift
            run_pipeline_local "$@"
            ;;
        "run-aws")
            shift
            run_pipeline_aws "$@"
            ;;
        "all")
            all
            ;;
        "shell")
            go_to_directory_src
            ;;
        *)
            help
            exit 1
            ;;
    esac
fi
