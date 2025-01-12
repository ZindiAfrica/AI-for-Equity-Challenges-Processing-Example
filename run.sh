#!/bin/bash
 set -e

 SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
 export SCRIPT_DIR

 export APP_NAME="sua-outsmarting-outbreaks"
 export APP_DIR="$SCRIPT_DIR/code/src"

 # Common functions for ML Pipeline script

 # Function to display usage
 usage() {
     echo "Usage: $0 [command] [options]"
     echo ""
     echo "Commands:"
     echo "  install              - Install dependencies"
     echo "  run [options]        - Run the ML pipeline"
     echo "  all                  - Install and run"
     echo ""
     echo "Options:"
     echo "  --debug             - Run in debug mode"
     echo ""
     echo "Example:"
     echo "  $0 install          # Only install dependencies"
     echo "  $0 run             # Run pipeline"
     echo "  $0 run --debug     # Run in debug mode"
     echo "  $0                  # Interactive mode"
     exit 1
 }

 # Function to install dependencies
 install_dependencies() {
     echo "Installing dependencies..."
     cd "$APP_DIR"
     uv venv
     source .venv/bin/activate
     uv pip install -e ".[dev]"
     pre-commit install
     echo "Dependencies installed successfully"
 }

 # Function to run the pipeline
 run_pipeline() {
     local debug=""
     # Parse additional arguments
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
         python -m sua_outsmarting_outbreaks.debug_entry
     else
         python build_and_run_aws.py
     fi
     echo "Pipeline completed successfully"
 }

 # Main execution function
 run_main() {
     if [ $# -eq 0 ]; then
         PS3="Please select an option (1-4): "
         options=("Install Dependencies" "Run Pipeline" "Install and Run" "Quit")
         select opt in "${options[@]}"
         do
             case $opt in
                 "Install Dependencies")
                     install_dependencies
                     break
                     ;;
                 "Run Pipeline")
                     run_pipeline
                     break
                     ;;
                 "Install and Run")
                     install_dependencies
                     run_pipeline
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
             "install")
                 install_dependencies
                 ;;
             "run")
                 shift  # Remove 'run' from arguments
                 run_pipeline "$@"  # Pass remaining arguments to run_pipeline
                 ;;
             "all")
                 install_dependencies
                 run_pipeline
                 ;;
             *)
                 usage
                 ;;
         esac
     fi
 }

 # Run main function with all arguments
 run_main "$@"
