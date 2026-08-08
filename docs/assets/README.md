# Screenshot plan

No screenshots are committed yet. The placeholders in the main README are intentional: visual evidence should be captured from a clean, current build rather than mocked.

Recommended assets:

| Filename | Capture | Acceptance criteria |
|---|---|---|
| `cli-build.png` | `generate-example`, `build`, `validate`, and `stats` | Current release, readable terminal, no personal path or machine identity |
| `events.png` | Pretty-printed synthetic event output | Rule name, severity, interval, and evidence visible; no claim of ground truth |
| `statistics.png` | Synthetic `statistics/summary.json` output | Flight/sample/event counts visible; identified as synthetic |
| `dataset-tree.png` | Generated directory tree | Matches the documented layout; no generated binary data committed |

Before committing an image:

1. build from the documented synthetic fixture at the commit being illustrated;
2. crop usernames, home directories, terminal history, tokens, and unrelated applications;
3. remove EXIF and other metadata;
4. use descriptive alt text and a stable filename;
5. record the source commit in the pull request;
6. update or remove the corresponding HTML placeholder in `README.md`.

Screenshots are explanatory assets, not compatibility or benchmark evidence.
