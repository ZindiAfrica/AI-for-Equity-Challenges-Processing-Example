"""Tests for AWS utility functions."""

from sua_outsmarting_outbreaks.utils.aws_utils import get_data_bucket_name


def test_get_data_bucket_name() -> None:
    """Test get_data_bucket_name returns expected bucket name."""
    bucket_name = get_data_bucket_name()
    assert isinstance(bucket_name, str)
    assert bucket_name == "sua-outsmarting-outbreaks-challenge-comp"
