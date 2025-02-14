"""Constants used throughout the project."""

from sua_outsmarting_outbreaks.utils.config import settings

# AWS SageMaker instance configurations
DEFAULT_INSTANCE_TYPE = settings.sagemaker.instance_type
DEFAULT_INSTANCE_COUNT = settings.sagemaker.instance_count
MAX_RUNTIME_SECONDS = 86400  # 24 hours
VOLUME_SIZE_GB = settings.sagemaker.volume_size
SPOT_INSTANCE = settings.sagemaker.use_spot
MAX_WAIT_TIME = settings.sagemaker.max_wait

# Instance specifications for different SageMaker instance types
INSTANCE_SPECS = {
    "ml.g4dn.8xlarge": {
        "gpu": "NVIDIA T4 with 16GB memory",
        "cpu_ram": "32 vCPUs, 128GB RAM",
        "network": "50 Gigabit",
        "storage": "9500 MBps EBS bandwidth, 40K IOPS",
        "cost": {
            "on_demand": 2.72,
            "spot": 0.816
        }
    },
    "ml.m5.2xlarge": {
        "gpu": "None",
        "cpu_ram": "8 vCPUs, 32GB RAM",
        "network": "Up to 10 Gigabit",
        "storage": "2300 MBps EBS bandwidth",
        "cost": {
            "on_demand": 0.46,
            "spot": 0.138
        }
    }
}

# Framework settings
SKLEARN_VERSION = settings.model.framework_version
AWS_REGION = settings.aws.region
DOCKER_IMAGE_TAG = "outsmarting-pipeline"
FRAMEWORK_NAME = settings.model.framework

# S3 paths and prefixes
MODEL_S3_PATH = "models/random_forest_model.joblib"
PREDICTIONS_PATH = "predictions/Predictions.csv"
DATA_PREP_OUTPUT = "data_prep/"
TRAINING_OUTPUT = "training/"
EVALUATION_OUTPUT = "evaluation/"
PREDICTIONS_OUTPUT = "predictions/"
MODEL_ARTIFACTS_PREFIX = "model-artifacts/"
LOGS_PREFIX = "logs/"

# Script paths
DATA_PREP_SCRIPT = "sua_outsmarting_outbreaks/data/data_prep.py"
MODEL_TRAINING_SCRIPT = "sua_outsmarting_outbreaks/models/train.py"
MODEL_EVALUATION_SCRIPT = "sua_outsmarting_outbreaks/models/evaluate.py"
MODEL_PREDICTION_SCRIPT = "sua_outsmarting_outbreaks/predict/predict.py"

# Model settings
TARGET_COLUMN = "Total"
EXCLUDED_COLUMNS = ["ID", "Location"]
RANDOM_SEED = 42
MODEL_VERSION = settings.model.version
BATCH_SIZE = settings.model.batch_size
NUM_WORKERS = settings.model.num_workers

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Default tags
DEFAULT_TAGS = [
    {"Key": "Environment", "Value": settings.environment},
    {"Key": "Project", "Value": settings.project_name},
    {"Key": "ManagedBy", "Value": "sagemaker"},
]
