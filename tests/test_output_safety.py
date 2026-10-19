from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, TextIO, cast

import pytest

from comic_gap_finder.cli import main
from comic_gap_finder.markdown import literal
from comic_gap_finder.output import validate_outputs, write_report, write_stdout


def test_existing_pair_and_duplicate_outputs(tmp_path: Path) -> None:
    existing = tmp_path / "existing"
    existing.write_bytes(b"keep")
    fresh = tmp_path / "fresh"
    assert main([str(tmp_path), "--json", str(fresh), "--markdown", str(existing)]) == 2
    assert existing.read_bytes() == b"keep"
    assert not fresh.exists()
    with pytest.raises(ValueError, match="distinct"):
        validate_outputs([fresh, fresh])
    with pytest.raises(OSError):
        write_report(existing, "replace")


def test_dangling_symlink(tmp_path: Path) -> None:
    target = tmp_path / "absent"
    link = tmp_path / "link"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable")
    with pytest.raises(OSError):
        validate_outputs([link])
    with pytest.raises(OSError):
        write_report(link, "replace")
    assert not target.exists()


def test_racing_file_is_preserved(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "race"
    original = Path.open

    def raced(self: Path, *args: Any, **kwargs: Any) -> TextIO:
        if self == path and args and args[0] == "x":
            with original(self, "w") as stream:
                stream.write("other writer")
        return cast(TextIO, original(self, *args, **kwargs))

    monkeypatch.setattr(Path, "open", raced)
    with pytest.raises(OSError):
        write_report(path, "report")
    assert path.read_text() == "other writer"


def test_utf8_and_stdout(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_report(None, "café\n")
    assert capsys.readouterr().out == "café\n"
    path = tmp_path / "new"
    write_report(path, "café\n")
    assert path.read_bytes() == "café\n".encode()


@pytest.mark.parametrize("failure", [BrokenPipeError("closed"), OSError(22, "closed")])
def test_stdout_failure(failure: OSError, monkeypatch: pytest.MonkeyPatch) -> None:
    class Broken:
        def write(self, text: str) -> int:
            raise failure

        def fileno(self) -> int:
            raise ValueError("no descriptor")

    monkeypatch.setattr(sys, "stdout", Broken())
    with pytest.raises(OSError):
        write_stdout("report")


def test_real_closed_stdout(tmp_path: Path) -> None:
    read_fd, write_fd = os.pipe()
    os.close(read_fd)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "comic_gap_finder", str(tmp_path)],
            stdout=write_fd,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    finally:
        os.close(write_fd)
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    assert "Exception ignored" not in result.stderr


def test_literal_fences_and_line_breaks() -> None:
    assert literal("a`b") == "``a`b``"
    assert literal("`edge`") == "`` `edge` ``"
    assert literal("x\n# forged") == r"`x\n# forged`"


def test_symlink_loops_are_cli_errors(tmp_path: Path) -> None:
    link = tmp_path / "loop"
    try:
        link.symlink_to(link.name)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable")
    assert main([str(link)]) == 2
    assert main([str(tmp_path), "--json", str(link)]) == 2
    assert main([str(tmp_path), "--json", str(link / "report.json")]) == 2
