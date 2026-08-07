# Contributing

Contributions are welcome from PX4/ROS 2 developers, researchers, students, data engineers, and documentation writers.

## Start safely

Search issues first. For behavioral/schema changes, open a Discussion or design issue before a large implementation. Never upload a log containing coordinates, identifiers, operator text, customer data, classified/export-controlled material, or data you cannot redistribute. Synthetic reproduction is preferred; read [Privacy and data governance](docs/PRIVACY.md).

## Development

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
make check
```

Generate a deterministic local fixture with `px4-dataset generate-example`. Do not commit generated datasets or ULogs unless an issue explicitly approves a fixture and provenance sidecar.

## Pull-request requirements

- Explain the user problem, scope, alternatives, and compatibility impact.
- Keep parsing, normalization, synchronization, events, quality, privacy, splitting, and export separate.
- Add complete typing and tests for success, missing data, and failure.
- Document units, source uORB fields, PX4-version evidence, interpolation, sensitivity, and conversion loss.
- Avoid safety/anomaly ground-truth claims for configurable rule events.
- Run `make check` and add a DCO sign-off to every commit: `git commit --signoff`.
- Confirm no proprietary algorithm, threshold, code, dataset, secret, or unauthorized third-party IP is included.

By contributing, you license the contribution under Apache-2.0 and certify the [Developer Certificate of Origin 1.1](https://developercertificate.org/). No copyright assignment is required.

## Review standard

Review the work, not the person. Mark blocking feedback clearly and tie it to a reproducible risk. Schema breaks require a migration note and architecture decision. Performance changes need peak-memory/runtime evidence. Privacy-sensitive changes require a threat/risk note and must keep local-only behavior.
