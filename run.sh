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
    uv venv
    source .venv/bin/activate
    uv pip install -e ".[dev]"
    uv pip install pytest pytest-cov
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

run_prepare() {
    echo "Running data preparation step..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python run_pipeline.py --stage prepare "$@"
}

run_train() {
    echo "Running model training step..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python run_pipeline.py --stage train "$@"
}

run_evaluate() {
    echo "Running model evaluation step..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python run_pipeline.py --stage evaluate "$@"
}

run_predict() {
    echo "Running prediction step..."
    cd "$APP_DIR"
    source .venv/bin/activate
    if [ $# -eq 0 ]; then
        python run_pipeline.py --stage prepare
    else
        python run_pipeline.py --stage prepare "$@"
    fi
}

run_pipeline() {
    echo "Running full pipeline..."
    cd "$APP_DIR"
    source .venv/bin/activate
    if [ $# -eq 0 ]; then
        python run_pipeline.py --stage all
    else
        python run_pipeline.py --stage all "$@"
    fi
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
    echo "  run [options]            - Run the ML pipeline"
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
        "Run Data Preparation"
        "Run Model Training"
        "Run Model Evaluation"
        "Run Predictions"
        "Run Full Pipeline"
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
            "Run Data Preparation")
                run_prepare
                show_menu
                ;;
            "Run Model Training")
                run_train
                show_menu
                ;;
            "Run Model Evaluation")
                run_evaluate
                show_menu
                ;;
            "Run Predictions")
                run_predict
                show_menu
                ;;
            "Run Full Pipeline")
                run_pipeline
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
        "run-evaluate")
            shift
            run_evaluate "$@"
            ;;
        "download")
            shift
            download_data "$@"
            ;;
        "run-prepare")
            shift
            run_prepare "$@"
            ;;
        "run-train")
            shift
            run_train "$@"
            ;;
        "run-predict")
            shift
            run_predict "$@"
            ;;
        "run")
            shift
            run_pipeline "$@"
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
