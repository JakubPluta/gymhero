import csv
from pathlib import Path

EXERCISES_CSV = Path(__file__).resolve().parents[2] / "resources" / "exercises.csv"

# Cells that stand for "no value" in the source CSV and should become NULLs.
_BLANKS = {"", "nan", "N/A"}

type ExerciseRow = dict[str, str | None]


def load_exercises() -> list[ExerciseRow]:
    """Load exercise rows from the seed CSV, de-duplicated by title.

    Blank / placeholder cells are normalised to ``None`` so seeded rows carry
    real NULLs instead of empty strings.
    """
    rows: list[ExerciseRow] = []
    seen: set[str] = set()
    with EXERCISES_CSV.open(newline="", encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            title = raw["Title"]
            if title in seen:
                continue
            seen.add(title)
            rows.append({k: (None if v in _BLANKS else v) for k, v in raw.items()})
    return rows


def unique_values(rows: list[ExerciseRow], col: str) -> list[str]:
    """Distinct non-null values of ``col`` in first-seen order."""
    ordered: dict[str, None] = {}
    for row in rows:
        value = row[col]
        if value is not None:
            ordered.setdefault(value, None)
    return list(ordered)
