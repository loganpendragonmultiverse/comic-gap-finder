from pathlib import Path
from typing import Any

import pytest

from comic_gap_finder.cli import main
from comic_gap_finder.core import parse_filename, scan_directory
from comic_gap_finder.render import render_markdown


def test_unicode_series_are_separate(tmp_path: Path) -> None:
    for name in ["物語 #1.cbz", "別話 #3.cbz"]:
        (tmp_path / name).touch()
    report = scan_directory(tmp_path, expectations={"物語": {"start": 1, "end": 2}})
    assert len(report.series) == 2
    by_name = {s.name: s for s in report.series}
    assert by_name["物語"].missing == [2]
    assert by_name["別話"].missing == []


@pytest.mark.parametrize("name", ["Series #1-3.cbz", "Series #1.2.3.cbz", "Series #1 #2.cbz"])
def test_compound_explicit_numbers_are_ambiguous(name: str) -> None:
    parsed, reason = parse_filename(Path(name))
    assert parsed is None
    assert reason


def test_legitimate_hyphen_and_decimal() -> None:
    parsed, _ = parse_filename(Path("North-South #1.5.cbz"))
    assert parsed and parsed.series == "North South" and str(parsed.issue) == "1.5"


@pytest.mark.parametrize(
    "raw",
    [
        '{"A":{"start":1,"end":2},"A":{"start":3,"end":4}}',
        '{"A":{"start":1,"start":2,"end":3}}',
        '{"A":{"start":1,"end":3,"omissions":{"2":"one","2":"two"}}}',
    ],
)
def test_duplicate_json_keys_rejected(tmp_path: Path, raw: str) -> None:
    config = tmp_path / "rules.json"
    config.write_text(raw)
    output = tmp_path / "new.json"
    assert main([str(tmp_path), "--expectations", str(config), "--json", str(output)]) == 2
    assert not output.exists()


def test_scan_does_not_open_content(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "Series #1.cbz").touch()

    def forbidden(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("scanner opened file contents")

    monkeypatch.setattr(Path, "open", forbidden)
    assert len(scan_directory(tmp_path).series) == 1


def test_literal_omission_reason(tmp_path: Path) -> None:
    report = scan_directory(
        tmp_path,
        expectations={
            "A`B": {"start": 1, "end": 2, "omissions": {"2": "Keep `literal`\n# not a heading"}}
        },
    )
    text = render_markdown(report)
    assert "## ``A`B``" in text
    assert r"``Keep `literal`\n# not a heading``" in text


def test_long_decimals_do_not_round_into_integer_issues(tmp_path: Path) -> None:
    for name in [
        "Series #1.cbz",
        "Series #1.0000000000000000000000000001.cbz",
        "Series #2.9999999999999999999999999999.cbz",
    ]:
        (tmp_path / name).touch()
    series = scan_directory(tmp_path).series[0]
    assert series.duplicates == {}
    assert series.non_integer_issues == [
        "1.0000000000000000000000000001",
        "2.9999999999999999999999999999",
    ]


def test_unidentified_punctuation_series_stays_ambiguous() -> None:
    parsed, reason = parse_filename(Path("!!! #1.cbz"))
    assert parsed is None
    assert "series name" in reason


@pytest.mark.parametrize(
    "name",
    [
        "Series #1 - 3.cbz",
        "Series #1–3.cbz",
        "Series #1 – 3.cbz",
        "Series #1—3.cbz",
        "Series #1 — 3.cbz",
    ],
)
def test_spaced_and_unicode_issue_ranges_stay_ambiguous(name: str) -> None:
    parsed, reason = parse_filename(Path(name))
    assert parsed is None
    assert "range" in reason


@pytest.mark.parametrize("name", ["Series #1 (2026).cbz", "Series #1 - Variant.cbz"])
def test_year_and_variant_are_not_ranges(name: str) -> None:
    parsed, _ = parse_filename(Path(name))
    assert parsed and str(parsed.issue) == "1"
