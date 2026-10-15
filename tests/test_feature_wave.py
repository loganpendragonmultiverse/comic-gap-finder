import json
from pathlib import Path
from typing import Any

import pytest

from comic_gap_finder.cli import main
from comic_gap_finder.core import scan_directory
from comic_gap_finder.render import render_markdown


def test_ranges_omissions_and_unobserved_series(tmp_path: Path) -> None:
    for name in ("A #1.cbz", "A #3.cbz", "A #2.5.cbz", "A Annual #1.cbz", "A #1 #2.cbz"):
        (tmp_path / name).touch()
    rules: dict[str, object] = {
        "A": {"start": 1, "end": 4, "omissions": {"2": "Not published"}},
        "Absent": {"start": 1, "end": 2},
    }
    report = scan_directory(tmp_path, expectations=rules)
    by_name = {s.name: s for s in report.series}
    assert by_name["A"].missing == [4]
    assert by_name["A"].non_integer_issues == ["2.5"]
    assert by_name["A Annual"].missing == []
    assert by_name["Absent"].missing == [1, 2]
    assert len(report.ambiguous) == 1
    assert "Not published" in render_markdown(report)
    assert by_name["A"].to_dict()["intentionalOmissions"] == {"2": "Not published"}
    assert scan_directory(tmp_path).series[0].missing == [2]
    config = tmp_path / "expectations.json"
    config.write_text(json.dumps(rules))
    assert main([str(tmp_path), "--expectations", str(config), "--fail-on-gaps"]) == 1


@pytest.mark.parametrize(
    "rule",
    [
        {"start": 4, "end": 1},
        {"start": 1.5, "end": 3},
        {"start": True, "end": 3},
        {"start": 1, "end": 1000000000},
        {"start": 1},
        {"start": 1, "end": 3, "typo": 1},
        {"start": 1, "end": 3, "omissions": []},
        {"start": 1, "end": 3, "omissions": {"2.5": "fraction"}},
        {"start": 1, "end": 3, "omissions": {"4": "outside"}},
        {"start": 1, "end": 3, "omissions": {"2": " "}},
        {"start": 1, "end": 3, "omissions": {"2": "a", "02": "b"}},
    ],
)
def test_invalid_rules(tmp_path: Path, rule: Any) -> None:
    with pytest.raises((ValueError, TypeError)):
        scan_directory(tmp_path, expectations={"A": rule})


def test_invalid_configuration_and_global_bounds(tmp_path: Path) -> None:
    data: Any
    for data in ([], {"": {}}, {"A": {}}, {"A": {"start": 1, "end": 3}, "a!": {}}):
        with pytest.raises((ValueError, TypeError)):
            scan_directory(tmp_path, expectations=data)
    with pytest.raises((ValueError, TypeError)):
        scan_directory(tmp_path, expected_end=10**9)
    report = scan_directory(tmp_path, expectations={"A": {"start": -1000, "end": 100000}})
    assert len(report.series[0].missing) == 101001
    bad = tmp_path / "bad.json"
    bad.write_text("[]")
    assert main([str(tmp_path), "--expectations", str(bad)]) == 2
