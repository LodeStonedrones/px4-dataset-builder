# Changelog

All notable changes follow Keep a Changelog and Semantic Versioning principles.

## [Unreleased]

### Added

- Added evidence-based compatibility tables, four Mermaid architecture and processing diagrams, benchmark and screenshot protocols, research citation metadata, contributor recognition, governance, and contributor onboarding documentation.
- Added dedicated dataset-contribution and documentation issue forms plus safe issue-routing links.
- Added manifest 1.1 provenance with the effective configuration, SHA-256 hashes, and artifact sizes.

### Changed

- Clarified alpha installation, compatibility evidence, ecosystem relationship, trademark status, community strategy, and performance limits.
- Reorganized privacy and methodology documentation under purpose-specific directories and reduced the first-dataset quick start to three copyable command lines.
- Updated supported dependency ranges and GitHub Actions versions already validated by Dependabot CI.
- Scoped release permissions to the publishing job and grouped future GitHub Actions updates.
- Build datasets in sibling staging directories and install them only after successful completion.
- Verify built wheels, container startup, release tag/version agreement, and distribution metadata in CI.

### Fixed

- Honor `output_directory` from configuration when `--output` is omitted.
- Redact failed input paths when anonymization is enabled.
- Validate every file referenced by the dataset manifest.
- Refuse destructive output paths that contain the source ULog or source directory.
- Remove unpaired absolute GPS coordinates and UTC reference metadata during anonymization.
- Keep normalized grids within the recorded duration and enforce interpolation gaps exactly.
- Skip duplicate ULog content safely and reject silent signal or event-rule configuration errors.
- Reject false edge events adjacent to missing values and count incomplete flights rather than issues.
- Use stable corpus-independent flight splits and conservative grouping when drone/date identity is absent.
- Remove semantically invalid course-over-ground and commander-state fallbacks.

### Security

- Enabled GitHub Private Vulnerability Reporting and documented safe reporting.
- Enabled Dependabot vulnerability alerts and automated security updates.
- Added Git ignore coverage and guidance for generated CSV and JSON Lines datasets.
- Bound normalized output rows and reject signed timestamp overflow before allocation.
- Validate metadata identity and artifact checksum/size evidence.

## [0.1.0] - 2026-08-07

### Added

- Local PyULog parsing for one or recursive ULog inputs.
- Canonical PX4 signal catalog and gap-aware resampling.
- Configurable threshold/change/edge/gap events.
- Quality checks, flight/group splits, anonymization, aggregate statistics.
- CSV, JSON Lines, and Zstandard Parquet datasets with a versioned manifest.
- Typer CLI, deterministic synthetic ULog, tests, Docker, CI, release workflow, and governance.
