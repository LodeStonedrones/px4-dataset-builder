# Contributing

Contributions are welcome from PX4 and ROS 2 developers, researchers, students, data engineers, privacy reviewers, and technical writers.

Start with the [Contributor onboarding guide](docs/community/CONTRIBUTOR_GUIDE.md). It explains contribution paths, flight-log handling, privacy expectations, dataset licensing, and the development workflow.

## Start safely

Search issues and Discussions before beginning work. For behavioral, dependency, methodology, or schema changes, open a Discussion or design issue before a large implementation.

Never upload a log containing coordinates, identifiers, operator text, customer data, classified or export-controlled material, accident-investigation data, proprietary information, or data you cannot redistribute. Opening an issue does not authorize file transfer. Synthetic reproduction is preferred; read [Privacy and data governance](docs/privacy/PRIVACY.md).

Use the dedicated forms for a [bug](https://github.com/LodeStonedrones/px4-dataset-builder/issues/new?template=bug.yml), [feature](https://github.com/LodeStonedrones/px4-dataset-builder/issues/new?template=feature.yml), [dataset contribution](https://github.com/LodeStonedrones/px4-dataset-builder/issues/new?template=dataset.yml), or [documentation improvement](https://github.com/LodeStonedrones/px4-dataset-builder/issues/new?template=documentation.yml).

## Development

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
make check
```

Generate a deterministic local fixture with `px4-dataset generate-example`. Do not commit generated datasets or ULogs unless an issue explicitly approves a fixture and its provenance sidecar.

## Scope and architecture

Preserve the existing module boundaries described in [Architecture](docs/architecture/ARCHITECTURE.md):

- keep PX4/PyULog mechanics inside parsing and topic adapters;
- keep canonical models and deterministic policies independent from file formats;
- keep parsing, normalization, synchronization, events, quality, anonymization, splitting, statistics, and export separately testable;
- avoid cloud requirements, hidden network behavior, proprietary logic, and learned models in the core;
- add dependencies only when a measured or documented requirement justifies them.

## Pull-request requirements

- Explain the user problem, scope, alternatives, and compatibility impact.
- Keep changes focused; do not combine unrelated refactoring and behavior.
- Add complete typing and tests for success, missing-data, and failure paths.
- Document units, source uORB fields, PX4-version evidence, interpolation, sensitivity, and conversion loss.
- Describe rule output as evidence, not safety or anomaly ground truth.
- Update compatibility, benchmark, and roadmap claims only when the pull request includes appropriate evidence.
- Run `make check` and add a DCO sign-off to every commit with `git commit --signoff`.
- Confirm no proprietary algorithm, threshold, code, dataset, secret, or unauthorized third-party IP is included.

By contributing, you license the contribution under Apache-2.0 and certify the [Developer Certificate of Origin 1.1](https://developercertificate.org/). No copyright assignment is required. Apache-2.0 applies to software contributions; contributed data requires separate, explicit terms.

## Review standard

Review the work, not the person. Mark blocking feedback clearly and tie it to a reproducible risk. Schema breaks require a migration note and architecture decision. Performance changes need public peak-memory and runtime evidence. Privacy-sensitive changes require a threat or risk note and must preserve local-only behavior.

Maintainers may close proposals that conflict with project scope, cannot be evaluated from public evidence, or create unacceptable privacy, licensing, security, or maintenance risk.
