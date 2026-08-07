# Roadmap and milestones

Roadmap versions describe exit criteria, not promised dates. Compatibility, privacy, and documentation are part of every milestone.

## v0.1 — ULog to tabular MVP

- Single/multi-log discovery and PyULog parsing.
- Canonical catalog, synchronization, CSV/JSONL/Parquet.
- Metadata, rule events, quality report, statistics, split, anonymization.
- Synthetic ULog, tests, CLI, Docker, CI, governance.

The implementation in this repository deliberately delivers more of the foundation than the original “parser + CSV” milestone so later releases share one schema.

## v0.2 — Compatibility and provenance

- Public ULog fixture matrix for supported PX4 releases.
- Reproducibility manifest with config digest and input-hash policy.
- Detailed missing-signal/applicability report.
- Incremental cache keyed by source hash, tool version, and configuration.
- Chunked processing benchmark for long/high-rate logs.

## v0.3 — Event semantics

- Rule schema versioning and event unit validation.
- Hysteresis/cooldown primitives that remain transparent.
- Additional public PX4 state transitions with release-aware enum maps.
- Event review tables and golden fixtures.

## v0.4 — Columnar analytics

- Stable Arrow schema and optional Arrow IPC export.
- Polars/DuckDB benchmark for lazy multi-flight statistics.
- Quantile/histogram summaries without loading all samples.
- Automatic dataset card in Markdown/HTML.

## v0.5 — Split audit

- Explicit group-key report and cross-split leakage scanner.
- Multi-label iterative event stratification.
- Time-forward/firmware-forward evaluation policies.
- Split manifest reuse across rebuilds.

## v0.6 — Privacy hardening

- Redaction preview/diff and configurable source-hash removal or keyed pseudonyms.
- Metadata risk scanner and policy presets.
- Coordinate/time transformation audit.
- Independent privacy review and public threat model.

## v0.7 — Quality and scale

- Version-aware sampling-rate expectations.
- Truncated/corrupt log recovery policy with explicit fidelity status.
- Property/fuzz tests for malformed ULog input.
- 100/1,000-log public synthetic benchmark and memory budgets.

## v0.8 — Interchange adapters

- ROS 2 bag and MCAP writers behind optional dependencies.
- HDF5 writer only with a documented schema/fidelity contract.
- Round-trip and dropped-field reports.

## v0.9 — Ecosystem beta

- Read-only dataset browser and local dashboard.
- Hugging Face dataset-card/export package generation, never automatic upload.
- Flight Review integration proposal or sidecar links after maintainer feedback.
- Dataset registry design with local catalogs first.

## v1.0 — Stable public release

- Stable canonical schema and migration policy.
- Semantic-versioned Python/CLI contracts.
- Supported PX4 release matrix and deprecation windows.
- Security/privacy review, reproducible releases, SBOM and signed artifacts.
- Complete tutorials for research, debugging, and ML leakage prevention.

## Later research, kept outside the core

ArduPilot DataFlash and raw MAVLink readers can share the output manifest but require independent source catalogs. A PX4 plugin may export recommended logging profiles, never control logic. Cloud processing, registries, and collaborative dashboards remain opt-in deployments with separate threat models. Learned anomaly detectors belong in downstream repositories consuming exported datasets, not in the reference builder.

## Initial GitHub backlog

| Issue | Labels | Milestone | Acceptance |
|---|---|---|---|
| Add PX4 v1.14–v1.16 authorized fixtures | `area:parser`, `needs-data`, `privacy` | v0.2 | Provenance sidecars and schema inventory pass CI |
| Publish manifest JSON Schema | `area:schema`, `help-wanted` | v0.2 | Valid/invalid fixtures and CI validation |
| Add config/input digest | `area:provenance` | v0.2 | Rebuild can prove equivalent inputs/policy |
| Add analyzer applicability table | `area:quality`, `good-first-issue` | v0.2 | Missing candidate has explicit reason |
| Validate PX4 navigation-state enum by release | `area:events`, `needs-px4-review` | v0.3 | Public-source mapping and golden tests |
| Benchmark Pandas versus Polars extraction | `area:performance` | v0.4 | Reproducible peak-RSS/runtime results |
| Add cross-split group audit | `area:split`, `good-first-issue` | v0.5 | Validator fails on injected leakage |
| Build anonymization preview command | `area:privacy`, `help-wanted` | v0.6 | Shows removed/derived fields before writing |
| Fuzz ULog parser boundary | `area:security`, `area:parser` | v0.7 | Seed corpus and bounded crash reproductions |
| Design ROS 2 bag fidelity contract | `area:ros2`, `design` | v0.8 | Mapping/loss document accepted before code |
