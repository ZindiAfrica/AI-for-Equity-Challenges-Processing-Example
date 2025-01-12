"""Constants used throughout the project."""

# AWS SageMaker instance configurations
# DEFAULT_INSTANCE_TYPE = "ml.m5.2xlarge"  # 8 vCPU, 32 GiB RAM
# DEFAULT_INSTANCE_COUNT = 1
# MAX_RUNTIME_SECONDS = 86400  # 24 hours
# VOLUME_SIZE_GB = 100
# SPOT_INSTANCE = True  # Use spot instances by default
# MAX_WAIT_TIME = 3600  # Maximum time to wait for spot instances

# Framework settings
# SKLEARN_VERSION = "0.23-1"
# AWS_REGION = "us-east-2"
# DOCKER_IMAGE_TAG = "outsmarting-pipeline"
# FRAMEWORK_NAME = "sklearn"

# S3 paths and prefixes
# MODEL_S3_PATH = "models/random_forest_model.joblib"
# PREDICTIONS_PATH = "predictions/Predictions.csv"
# DATA_PREP_OUTPUT = "data_prep/"
# TRAINING_OUTPUT = "training/"
# EVALUATION_OUTPUT = "evaluation/"
# PREDICTIONS_OUTPUT = "predictions/"
# MODEL_ARTIFACTS_PREFIX = "model-artifacts/"
# LOGS_PREFIX = "logs/"

# Script paths
# DATA_PREP_SCRIPT = "sua_outsmarting_outbreaks/data/data_prep.py"
# MODEL_TRAINING_SCRIPT = "sua_outsmarting_outbreaks/models/train.py"
# MODEL_EVALUATION_SCRIPT = "sua_outsmarting_outbreaks/models/evaluate.py"
# MODEL_PREDICTION_SCRIPT = "sua_outsmarting_outbreaks/predict/predict.py"

# Model settings
# TARGET_COLUMN = "Total"
# EXCLUDED_COLUMNS = ["ID", "Location"]
# RANDOM_SEED = 42
# MODEL_VERSION = "1.0.0"
# BATCH_SIZE = 32
# NUM_WORKERS = 4

# Logging configuration
# LOG_LEVEL = "INFO"
# LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Default tags
# DEFAULT_TAGS = [
#     {"Key": "Environment", "Value": "development"},
#     {"Key": "Project", "Value": "sua-outsmarting-outbreaks"},
#     {"Key": "ManagedBy", "Value": "sagemaker"}
# ]
