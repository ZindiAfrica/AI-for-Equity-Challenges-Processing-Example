"""Tests for data preparation functionality."""

from pathlib import Path

from sua_outsmarting_outbreaks.data.data_prep import get_data_dir


def test_get_data_dir() -> None:
    """Test get_data_dir returns a Path object."""
    data_dir = get_data_dir()
    assert isinstance(data_dir, Path)
    assert data_dir.name == "data"
