# Requirements analysis

## Functional boundary

The MVP accepts one `.ulg` or a recursively scanned directory; parses selected uORB topics; produces a synchronized canonical table per flight; detects transparent events; validates quality; optionally anonymizes; assigns whole flights/groups to train, validation, and test; exports CSV, JSON Lines, or Parquet; and writes metadata, statistics, a quality report, a signal schema, and a global manifest.

ROS 2 bag, HDF5, Arrow IPC, web/cloud services, Flight Review, dataset publishing, ArduPilot, and raw MAVLink are extension points, not v0.1 behavior.

## Architectural problems identified

1. **PX4 schema drift.** Topic names, fields, enums, and estimator messages vary across releases. Resolution: an ordered data catalog maps only known public candidates and exports the mapping used.
2. **Asynchronous clocks.** A simple dataframe join either explodes row count or invents samples. Resolution: signal-specific, gap-bounded policies on a flight-relative grid.
3. **Methodological interpolation.** Flags, modes, angles, quaternions, and missing sensor intervals must not be treated like ordinary continuous scalars. Resolution: explicit per-signal policies; nearest quaternion samples; no long-gap bridging.
4. **Data leakage.** Random sample splits make train and test contain the same flight dynamics. Resolution: the flight is the minimum split unit; drone/date grouping is available.
5. **Scale.** Collecting hundreds of wide dataframes exhausts memory. Resolution: one-flight worker processing and immediate staging; only metadata and events stay in the coordinator.
6. **Corruption and partial logs.** Batch execution must continue while preserving failures. Resolution: per-file error boundaries, quality findings, and failed-log records in the manifest.
7. **Privacy.** GPS, timestamps, UUIDs, filenames, and free text can identify operations. Resolution: local-only defaults and an explicit anonymization layer after analysis and before export. A redaction preview is planned, not current v0.1 behavior.
8. **Labels are not truth.** Rule-based events can be configuration-dependent and correlated. Resolution: rules, values, thresholds, descriptions, and versions remain in the output; the project avoids anomaly/safety claims.
9. **Absolute time ambiguity.** ULog timestamps are normally boot-relative; `time_ref_utc` may be missing. Resolution: `time_s` is authoritative, and ISO dates are emitted only when credible UTC metadata exists.
10. **Small dataset splits.** Ratios cannot guarantee non-empty partitions for one or two groups. Resolution: preserve leakage boundaries and report the actual distribution instead of duplicating flights.

## Non-functional requirements

- Python 3.12+, full public typing, strict configuration validation.
- Deterministic rules/splits for identical inputs and configuration.
- No network calls or telemetry.
- Bounded per-worker memory proportional to one normalized flight.
- Explicit conversion loss/missingness and no silent topic substitution.
- Unit, integration, parser, event, anonymization, split, quality, CLI, and end-to-end tests.
- Apache-2.0, DCO, security policy, CI and release automation. Branch protection is recommended before multi-maintainer development.

## Acceptance evidence

The integration suite creates a binary ULog from the public format, parses it with PyULog, runs all default event/quality stages, emits all three formats, validates file references, and checks the anonymized coordinate path. No real flight is required in CI.
