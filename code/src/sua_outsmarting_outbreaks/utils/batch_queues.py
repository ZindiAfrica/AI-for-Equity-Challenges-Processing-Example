"""AWS Batch queue configuration and utilities."""

from dataclasses import dataclass
from typing import List

@dataclass
class BatchQueue:
    """AWS Batch queue configuration."""

    name: str
    region: str
    availability_zone: str

    @property
    def queue_arn(self) -> str:
        """Get the queue ARN."""
        return f"arn:aws:batch:{self.region}:869935100875:job-queue/{self.name}"

def get_batch_queues(region: str = "us-east-2") -> List[BatchQueue]:
    """Get list of available batch queues for a region.
    
    Args:
        region: AWS region name
        
    Returns:
        List of BatchQueue objects for the region
    """
    return [
        BatchQueue(
            name="main-compute-queue-us-east-2a",
            region=region,
            availability_zone="us-east-2a"
        ),
        BatchQueue(
            name="main-compute-queue-us-east-2b", 
            region=region,
            availability_zone="us-east-2b"
        ),
        BatchQueue(
            name="main-compute-queue-us-east-2c",
            region=region,
            availability_zone="us-east-2c"
        )
    ]

def get_queue_for_az(availability_zone: str, region: str = "us-east-2") -> BatchQueue:
    """Get batch queue for specific availability zone.
    
    Args:
        availability_zone: AWS availability zone
        region: AWS region name
        
    Returns:
        BatchQueue for the specified AZ
        
    Raises:
        ValueError: If no queue exists for the AZ
    """
    queues = get_batch_queues(region)
    for queue in queues:
        if queue.availability_zone == availability_zone:
            return queue
    raise ValueError(f"No batch queue found for AZ: {availability_zone}")
