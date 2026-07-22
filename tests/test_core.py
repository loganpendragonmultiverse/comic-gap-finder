from decimal import Decimal
from pathlib import Path

import pytest

from comic_gap_finder.core import (
    build_series_report,
    clean_series,
    decimal_issue,
    normalize_series,
    parse_filename,
    scan_directory,
)
from comic_gap_finder.models import ParsedComic


def touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"test")


def test_parses_explicit_and_single_number_filenames() -> None:
    explicit, _ = parse_filename(Path("Night Watch #012 (2024).cbz"))
    assert explicit and explicit.issue == Decimal(12)
    assert explicit.series == "Night Watch"
    plain, _ = parse_filename(Path("Night Watch 013 (2024).cbr"))
    assert plain and plain.issue == Decimal(13)
    assert plain.method == "single number token"


def test_excludes_year_and_volume_tokens() -> None:
    parsed, _ = parse_filename(Path("Night Watch v2 014 (2025).cbz"))
    assert parsed and parsed.issue == Decimal(14)
    missing, reason = parse_filename(Path("Night Watch v2 (2025).cbz"))
    assert missing is None
    assert "unique" in reason


def test_reports_ambiguous_multiple_numbers() -> None:
    parsed, reason = parse_filename(Path("Series 12 alternate 13.cbz"))
    assert parsed is None
    assert "unique" in reason
    parsed, reason = parse_filename(Path("Series #1 issue 2.cbz"))
    assert parsed is None
    assert "multiple explicit" in reason


def test_scans_groups_and_reports_gaps_duplicates_and_specials(tmp_path: Path) -> None:
    for name in [
        "Night Watch #1.cbz",
        "night-watch 002.cbr",
        "Night Watch #2 Variant.cbz",
        "Night Watch #4.cb7",
        "Night Watch #4.5.cbz",
    ]:
        touch(tmp_path / name)
    touch(tmp_path / "notes.txt")
    report = scan_directory(tmp_path)
    assert len(report.series) == 1
    series = report.series[0]
    assert series.missing == [3]
    assert "2" in series.duplicates
    assert series.non_integer_issues == ["4.5"]
    assert report.ignored == ["notes.txt"]


def test_expected_range_and_recursive_mode(tmp_path: Path) -> None:
    touch(tmp_path / "nested" / "Series #2.cbz")
    assert scan_directory(tmp_path).series == []
    report = scan_directory(tmp_path, recursive=True, expected_start=1, expected_end=3)
    assert report.series[0].missing == [1, 3]
    with pytest.raises(ValueError, match="greater"):
        scan_directory(tmp_path, expected_start=4, expected_end=3)


def test_rejects_missing_root(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not a directory"):
        scan_directory(tmp_path / "missing")


def test_helpers_are_conservative() -> None:
    assert decimal_issue("1.50") == Decimal("1.5")
    assert decimal_issue("100001") is None
    assert clean_series("[Series_Name]-variant") == "Series Name"
    assert normalize_series("Series: Name") == "seriesname"
    comic = ParsedComic(Path("Series #2.cbz"), "Series", Decimal(2), "test")
    report = build_series_report("Series", [comic], expected_start=None, expected_end=None)
    assert report.missing == []
