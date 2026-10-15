from pathlib import Path

from comic_gap_finder.cli import main
from comic_gap_finder.core import scan_directory
from comic_gap_finder.render import render_json, render_markdown


def test_renderers_and_cli_outputs(tmp_path: Path) -> None:
    (tmp_path / "Series #1.cbz").write_bytes(b"x")
    (tmp_path / "Series #3.cbz").write_bytes(b"x")
    report = scan_directory(tmp_path)
    assert '"missing": [' in render_json(report)
    assert "Missing: 2" in render_markdown(report)
    json_path = tmp_path / "out" / "report.json"
    markdown_path = tmp_path / "out" / "report.md"
    assert main([str(tmp_path), "--json", str(json_path), "--markdown", str(markdown_path)]) == 0
    assert main([str(tmp_path), "--fail-on-gaps"]) == 1
    assert main([str(tmp_path), "--json", str(json_path)]) == 2


def test_cli_reports_missing_root(tmp_path: Path) -> None:
    assert main([str(tmp_path / "missing")]) == 2
