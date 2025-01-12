#!/bin/bash
set -e
export AWS_PROFILE=zindicomp
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export APP_NAME="sua-outsmarting-outbreaks"
export APP_DIR="$SCRIPT_DIR/code/src"

# Required functions
install_dependencies() {
    echo "Installing dependencies..."
    cd "$APP_DIR"
    uv venv
    source .venv/bin/activate
    uv pip install -e ".[dev]"
    pre-commit install
    echo "Dependencies installed successfully"
}

build() {
    echo "Building Docker image..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python build_and_run_aws.py --build-only
}

test() {
    echo "Running tests..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python -m pytest tests/
}

package() {
    echo "Creating deployment package..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python build_and_run_aws.py --package-only
}

deploy() {
    echo "Deploying to AWS..."
    cd "$APP_DIR"
    source .venv/bin/activate
    python build_and_run_aws.py --deploy-only
}

go_to_directory() {
    cd "$APP_DIR"
    exec $SHELL
}

run() {
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
    install_dependencies
    build
    test
    package
    deploy
    run
}

help() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  help                - Display this help message"
    echo "  install             - Install dependencies"
    echo "  build              - Build Docker image"
    echo "  test               - Run test suite"
    echo "  package            - Create deployment package"
    echo "  deploy             - Deploy to AWS"
    echo "  run [options]      - Run the ML pipeline"
    echo "  all                - Run all steps in sequence"
    echo "  shell              - Open shell in project directory"
    echo ""
    echo "Options:"
    echo "  --debug            - Run in debug mode"
    echo ""
    echo "Example:"
    echo "  $0 install         # Only install dependencies"
    echo "  $0 run            # Run pipeline"
    echo "  $0 run --debug    # Run in debug mode"
    echo "  $0                # Interactive mode"
}

# Main execution
if [ $# -eq 0 ]; then
    PS3="Please select an option (1-10): "
    options=(
        "Help"
        "Install Dependencies" 
        "Build"
        "Test"
        "Package"
        "Deploy"
        "Run Pipeline"
        "Run All Steps"
        "Go to Directory"
        "Quit"
    )
    select opt in "${options[@]}"
    do
        case $opt in
            "Help")
                help
                break
                ;;
            "Install Dependencies")
                install_dependencies
                break
                ;;
            "Build")
                build
                break
                ;;
            "Test")
                test
                break
                ;;
            "Package")
                package
                break
                ;;
            "Deploy")
                deploy
                break
                ;;
            "Run Pipeline")
                run
                break
                ;;
            "Run All Steps")
                all
                break
                ;;
            "Go to Directory")
                go_to_directory
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
            install_dependencies
            ;;
        "build")
            build
            ;;
        "test")
            test
            ;;
        "package")
            package
            ;;
        "deploy")
            deploy
            ;;
        "run")
            shift
            run "$@"
            ;;
        "all")
            all
            ;;
        "shell")
            go_to_directory
            ;;
        *)
            help
            exit 1
            ;;
    esac
fi
