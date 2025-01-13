"""Utility functions for managing project directories."""

import os
from pathlib import Path

from sua_outsmarting_outbreaks.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

def get_project_root() -> Path:
    """Get the project root directory.
    
    Returns:
        Path to project root directory
    """
    # Walk up until we find the code/src directory structure
    current = Path(__file__).resolve()
    while current.name != "src" and current.parent != current:
        current = current.parent
    return current.parent.parent

def get_data_dir() -> Path:
    """Get the data directory path.
    
    Returns:
        Path to data directory
    """
    data_dir = get_project_root() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def get_output_dir() -> Path:
    """Get the output directory path.
    
    Returns:
        Path to output directory
    """
    output_dir = get_project_root() / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def get_models_dir() -> Path:
    """Get the models directory path.
    
    Returns:
        Path to models directory
    """
    models_dir = get_output_dir() / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir

def ensure_dir(path: str | Path) -> Path:
    """Ensure a directory exists and return its Path.
    
    Args:
        path: Directory path as string or Path
        
    Returns:
        Path object for the directory
    """
    dir_path = Path(path).resolve()
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def get_relative_to_project(path: str | Path) -> Path:
    """Convert a path to be relative to project root.
    
    Args:
        path: Path to convert
        
    Returns:
        Path relative to project root
    """
    return (get_project_root() / path).resolve()
