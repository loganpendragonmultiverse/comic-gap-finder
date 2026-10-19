# Development scope

Version 1 performs a read-only, metadata-free filename audit. Ambiguous filenames remain unresolved rather than guessed. Missing numbers are computed only within observed or explicitly requested integer ranges.

Archive contents, external databases, rename operations, and editorial claims about true completeness are outside this release.


## Version 1.1.0

Use `--expectations expectations.json` to apply a separate integer range to each named series:

```json
{"North Signal":{"start":1,"end":12,"omissions":{"7":"Number intentionally not collected"}}}
```

Series names use the existing normalized filename grouping. Duplicate normalized names are rejected. Each rule requires both bounds; it overrides the global range for that series. Configured series with no files are still reported. Omission reasons appear in JSON and Markdown and suppress only those missing integer numbers. They do not hide present files, duplicates, decimals, annuals, or ambiguous filenames. Global options and scans without a configuration keep their existing behavior. Bounds are limited to -1000 through 100000 (at most 101001 integer numbers per series). Decimal issues remain evidence, not integer range members. Annuals remain separate filename-inferred series; ambiguous identities require review.

## 1.1.2 acceptance

Keep distinct non-Latin series separate and leave explicit issue ranges unresolved.

- Preserve Unicode letters and digits in grouping and exact decimal issue values; quarantine compound explicit issue numbers and reject duplicate expectation JSON keys.
- Reserve report files exclusively, preflight paired destinations, and render titles, paths and omission reasons literally in Markdown.

Tests prove scanning uses names and file metadata without opening discovered file content. Exercise normal and ambiguous matches, malformed configuration, pre-existing/duplicate/dangling/racing output paths, real closed stdout, and Markdown containing backticks or line breaks. Preserve input bytes and the existing coverage floor. Run formatting, lint, strict typing for source and tests, the full suite and wheel/source builds. Reinstall the built distributions in isolation for CLI acceptance before release.

Paired output preflight avoids known collisions; exclusive creation protects later collisions. A later failure may leave a new partial report; no rollback deletion or power-loss transaction is promised.

The wheel includes the handoff documents under `share/comic-gap-finder` in the installation prefix; the source archive keeps them at its top level.
