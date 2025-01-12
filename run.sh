#!/bin/bash
set -e
export AWS_PROFILE=zindicomp
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export APP_NAME="sua-outsmarting-outbreaks"
export APP_DIR="$SCRIPT_DIR/code/src"

# Required functions with component suffixes
install_dependencies_python() {
    echo "Installing Python dependencies..."
    cd "$APP_DIR"
    uv venv
    source .venv/bin/activate
    uv pip install -e ".[dev]"
    pre-commit install
    echo "Dependencies installed successfully"
}

install_dependencies_all() {
    install_dependencies_python
}

build_docker() {
    echo "Building Docker image..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python build_and_run_aws.py --build-only
}

build_all() {
    build_docker
}

test_python() {
    echo "Running Python tests..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python -m pytest tests/
}

test_all() {
    test_python
}

package_docker() {
    echo "Creating Docker deployment package..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python build_and_run_aws.py --package-only
}

package_all() {
    package_docker
}

deploy_sagemaker() {
    echo "Deploying to AWS SageMaker..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python build_and_run_aws.py --deploy-only
}

deploy_all() {
    deploy_sagemaker
}

go_to_directory_src() {
    cd "$APP_DIR"
    exec $SHELL
}

go_to_directory_all() {
    go_to_directory_src
}

run_pipeline() {
    local debug=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --debug)
                debug="--debug"
                shift
                ;;
            *)
                echo "Unknown parameter: $1"
                return 1
                ;;
        esac
    done

    echo "Running ML pipeline${debug:+ in debug mode}..."
    cd "$APP_DIR"
    source .venv/bin/activate
    
    if [ -n "$debug" ]; then
        echo "Executing command: python -m sua_outsmarting_outbreaks.debug_entry"
        python -m sua_outsmarting_outbreaks.debug_entry
    else
        echo "Executing command: python build_and_run_aws.py"
        python build_and_run_aws.py
    fi
}

all() {
    install_dependencies_all
    build_all
    test_all
    package_all
    deploy_all
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

# Main execution
if [ $# -eq 0 ]; then
    PS3="Please select an option (1-15): "
    options=(
        "Help"
        "Install All Dependencies"
        "Install Python Dependencies"
        "Build All"
        "Build Docker Image"
        "Test All"
        "Run Python Tests"
        "Package All"
        "Package Docker Image"
        "Deploy All"
        "Deploy to SageMaker"
        "Run Pipeline"
        "Run All Steps"
        "Go to Source Directory"
        "Quit"
    )
    select opt in "${options[@]}"
    do
        case $opt in
            "Help")
                help
                break
                ;;
            "Install All Dependencies")
                install_dependencies_all
                break
                ;;
            "Install Python Dependencies")
                install_dependencies_python
                break
                ;;
            "Build All")
                build_all
                break
                ;;
            "Build Docker Image")
                build_docker
                break
                ;;
            "Test All")
                test_all
                break
                ;;
            "Run Python Tests")
                test_python
                break
                ;;
            "Package All")
                package_all
                break
                ;;
            "Package Docker Image")
                package_docker
                break
                ;;
            "Deploy All")
                deploy_all
                break
                ;;
            "Deploy to SageMaker")
                deploy_sagemaker
                break
                ;;
            "Run Pipeline")
                run_pipeline
                break
                ;;
            "Run All Steps")
                all
                break
                ;;
            "Go to Source Directory")
                go_to_directory_src
                break
                ;;
            "Quit")
                exit 0
                ;;
            *)
                echo "Invalid option $REPLY"
                ;;
        esac
    done
else
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
        "package")
            package_all
            ;;
        "package-docker")
            package_docker
            ;;
        "deploy")
            deploy_all
            ;;
        "deploy-sagemaker")
            deploy_sagemaker
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
