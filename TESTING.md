# Testing

## Feature-wave regression gate

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build` after installing `.[dev]` in an isolated environment. The focused regressions are in `tests/test_feature_wave.py`; run them together with the existing suite. Keep the configured coverage threshold. Repository CI supplies the supported OS/Python matrix.

## 1.1.2 acceptance

Keep distinct non-Latin series separate and leave explicit issue ranges unresolved.

- Preserve Unicode letters and digits in grouping and exact decimal issue values; quarantine compound explicit issue numbers and reject duplicate expectation JSON keys.
- Reserve report files exclusively, preflight paired destinations, and render titles, paths and omission reasons literally in Markdown.

Tests prove scanning uses names and file metadata without opening discovered file content. Exercise normal and ambiguous matches, malformed configuration, pre-existing/duplicate/dangling/racing output paths, real closed stdout, and Markdown containing backticks or line breaks. Preserve input bytes and the existing coverage floor. Run formatting, lint, strict typing for source and tests, the full suite and wheel/source builds. Reinstall the built distributions in isolation for CLI acceptance before release.

Paired output preflight avoids known collisions; exclusive creation protects later collisions. A later failure may leave a new partial report; no rollback deletion or power-loss transaction is promised.
