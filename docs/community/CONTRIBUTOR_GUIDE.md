# Contributor onboarding

PX4 Dataset Builder welcomes focused contributions that improve public interoperability, reproducibility, privacy, documentation, and verified compatibility. The core remains local-first and contains no proprietary flight logic.

## Choose a contribution path

### Code

Good first contributions include one documented uORB field mapping, one quality assertion, one synthetic regression fixture, one bounded CLI improvement, or one exporter test. Open an issue before changing a public schema or adding a dependency.

### Documentation

Clarify a command, unit, methodology choice, limitation, compatibility result, or privacy risk. Documentation claims need the same evidence standard as code claims. Use the [Documentation issue form](https://github.com/LodeStonedrones/px4-dataset-builder/issues/new?template=documentation.yml).

### Research and methodology

Propose reproducible resampling, splitting, quality, or benchmark methods in a Discussion before implementation. Describe assumptions, failure modes, alternatives, and the public evidence supporting the proposal.

### Flight data

Do not upload a log before completing the process below.

## Contributing flight data

Use the [Dataset Contribution issue form](https://github.com/LodeStonedrones/px4-dataset-builder/issues/new?template=dataset.yml) to describe the scenario without attaching the file or revealing sensitive details. Maintainers will choose one of three paths:

1. **Synthetic reproduction — preferred.** Create a minimal non-operational ULog that reproduces the format or behavior.
2. **Reviewed local inventory.** Run `px4-dataset inspect` locally and share only manually reviewed, non-sensitive topic/schema information.
3. **Authorized fixture.** Provide a deliberately releasable log with explicit ownership, redistribution, privacy, and retention terms.

Private investigation is exceptional. It requires a named maintainer, agreed purpose, encrypted transfer, deletion date, no cloud upload, no permanent test dependency, and deletion confirmation. Do not send a file merely because an issue was opened.

## Privacy expectations

Treat every ULog as sensitive until reviewed. ULogs and derived datasets can expose:

- coordinates, routes, UTC time, takeoff or landing sites;
- vehicle UUIDs, hardware, firmware branches, filenames, and operator text;
- mission states, failures, experimental procedures, and customer information;
- recognizable trajectory shape even after absolute coordinates are removed.

Contributors must have authority to use and share the input. Never submit classified, export-controlled, military, customer-confidential, accident-investigation, personally identifying, or commercially sensitive logs.

Built-in transformations can remove GPS, derive relative coordinates, remove timestamps, hash filenames, remove identity metadata, and redact messages. They reduce risk but cannot guarantee anonymity. Review every generated artifact manually.

## Dataset licensing

Apache-2.0 covers the software, not automatically the source logs or generated datasets. Every public fixture or dataset contribution needs separate terms that answer:

- who owns or controls the data;
- who authorized submission and redistribution;
- permitted research, commercial, and derivative use;
- attribution requirements;
- privacy/redaction steps and residual risks;
- whether withdrawal is possible before an immutable release;
- the responsible contact for questions.

Prefer a standard data license appropriate to the contributor's rights. Do not label a dataset Apache-2.0 merely because this software produced it.

## Development workflow

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
make check
```

Then:

1. create a focused branch;
2. add tests and documentation for observable behavior;
3. run `make check`;
4. inspect `git status` for generated logs or datasets;
5. sign off every commit with `git commit --signoff`;
6. open a pull request using the repository template.

The complete review requirements are in [CONTRIBUTING.md](../../CONTRIBUTING.md). All contributions are licensed under Apache-2.0 and certified under the Developer Certificate of Origin 1.1; no copyright assignment is required.
