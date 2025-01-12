"""Configuration management using Pydantic."""
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AWSConfig(BaseModel):
    """AWS-specific configuration."""
    region: str = Field(default="us-east-2", description="AWS region to use")
    profile: Optional[str] = Field(default=None, description="AWS profile name")
    data_bucket: str = Field(
        default="sua-outsmarting-outbreaks-challenge-comp",
        description="Main data bucket"
    )


class SageMakerConfig(BaseModel):
    """SageMaker-specific configuration."""
    instance_type: str = Field(
        default="ml.m5.2xlarge",
        description="Instance type for processing"
    )
    instance_count: int = Field(default=1, description="Number of instances")
    volume_size: int = Field(default=100, description="EBS volume size in GB")
    use_spot: bool = Field(default=True, description="Use spot instances")
    max_wait: int = Field(
        default=3600,
        description="Maximum wait time for spot instances"
    )


class ModelConfig(BaseModel):
    """Model training configuration."""
    batch_size: int = Field(default=32, description="Training batch size")
    num_workers: int = Field(default=4, description="Number of data workers")
    version: str = Field(default="1.0.0", description="Model version")
    framework: str = Field(default="sklearn", description="ML framework")
    framework_version: str = Field(default="0.23-1", description="Framework version")


class Settings(BaseSettings):
    """Main configuration settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

    # Sub-configurations
    aws: AWSConfig = Field(default_factory=AWSConfig)
    sagemaker: SageMakerConfig = Field(default_factory=SageMakerConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)

    # Project settings
    project_name: str = Field(
        default="sua-outsmarting-outbreaks",
        description="Project name"
    )
    environment: str = Field(
        default="development",
        description="Deployment environment"
    )

    # Paths
    base_dir: Path = Field(
        default=Path(__file__).parent.parent.parent,
        description="Base project directory"
    )

    @property
    def is_debug(self) -> bool:
        """Check if running in debug mode."""
        return self.environment == "development"


# Global settings instance
settings = Settings()
