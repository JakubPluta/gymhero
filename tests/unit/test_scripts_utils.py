import argparse

import pytest

from scripts.core.resources import load_exercises, unique_values
from scripts.core.seed import build_argparser


def test_load_exercises_returns_non_empty_rows():
    rows = load_exercises()
    assert len(rows) > 0
    assert set(rows[0]) >= {"Title", "Desc", "Type", "BodyPart", "Level"}


def test_load_exercises_deduplicates_titles():
    rows = load_exercises()
    titles = [row["Title"] for row in rows]
    assert len(titles) == len(set(titles))


def test_unique_values_preserves_first_seen_order_and_skips_none():
    rows = [
        {"Level": "Beginner"},
        {"Level": "Advanced"},
        {"Level": "Beginner"},
        {"Level": None},
    ]
    assert unique_values(rows, "Level") == ["Beginner", "Advanced"]


def test_build_argparser_accepts_valid_env_and_rejects_invalid():
    parser = build_argparser()
    assert isinstance(parser, argparse.ArgumentParser)

    assert parser.parse_args(["--env=dev"]).env == "dev"
    assert parser.parse_args(["--env=test"]).env == "test"

    with pytest.raises(SystemExit):
        parser.parse_args(["--env=invalid"])
