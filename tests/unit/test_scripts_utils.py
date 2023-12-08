import argparse

import pytest

from scripts.core.utils import get_argparser, load_exercise_resource


def test_load_exercise_resource():
    """Load the exercise resource and assert that the dataframe has
    more than 0 rows and more than 0 columns.
    """
    df = load_exercise_resource()
    assert len(df) > 0 and len(df.columns) > 0


def test_get_argparser():
    """Test that the get_argparser function returns an ArgumentParser object."""
    parser = get_argparser()

    assert isinstance(parser, argparse.ArgumentParser)
    args = parser.parse_args("--env=dev".split())
    assert getattr(args, "env") == "dev"

    args = parser.parse_args("--env=test".split())
    assert getattr(args, "env") == "test"

    with pytest.raises(SystemExit):
        parser.parse_args("--env=invalid".split())
