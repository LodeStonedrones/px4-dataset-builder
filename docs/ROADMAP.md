# Adoption-first roadmap

PX4 Dataset Builder is under a feature freeze. The core already converts ULogs into
synchronized, documented, privacy-aware datasets. New code is accepted only when it
removes a demonstrated adoption blocker or expands compatibility with evidence.

Roadmap items are exit criteria, not promised dates.

## Current gate — trustworthy alpha

- Transactional builds that preserve an existing dataset on failure.
- Manifested effective configuration and artifact checksum evidence.
- Strict configuration, privacy, split, event, and resampling regression tests.
- Wheel and container smoke tests plus release tag/version verification.
- Accurate documentation with no unmeasured performance or compatibility claims.

## Adoption gate — evidence before breadth

1. Collect redistributable PX4 release fixtures with provenance and privacy sidecars.
2. Validate and document current PX4 field mappings release by release.
3. Publish one small, non-operational example dataset and a copyable research workflow.
4. Publish measured runtime, peak-memory, and output-size results for that corpus.
5. Provide a local contribution/privacy preview that explains exactly what a proposed
   fixture bundle contains before a user shares anything.

The project should spend more effort on these five outcomes than on new output formats,
visualization, or integrations.

## Candidate code work

Only two feature families currently pass the adoption threshold:

- **Release-aware compatibility packs:** per-candidate PX4 field transformations,
  versioned fixture inventories, and generated compatibility evidence.
- **Contribution bundle preview:** a local, non-uploading command that validates consent
  metadata, previews privacy transformations, and creates a reviewable bundle.

Both require design issues, tests, and public evidence before implementation. Neither may
upload data or claim anonymous output.

## Explicitly deferred

- Dataset card generation may be reconsidered after real users produce datasets.
- Additional summary statistics require a concrete research request and schema review.
- Performance-engine changes require published measurements from the existing pipeline.
- ROS 2 workflows should initially document PyULog's maintained `ulog2ros2bag` converter
  rather than duplicate it.

## Not planned in the core

- Flight-health reports, anomaly scoring, learned models, or safety conclusions.
- Interactive timelines, automatic flight plots, flight comparison, or a desktop GUI.
- Web UI, REST API, hosted registry, cloud processing, telemetry, or automatic upload.
- HDF5, Arrow IPC, DuckDB, or other formats without a concrete consumer and fidelity
  contract; Parquet already covers the columnar research path.
- A plugin framework before a stable third-party extension need exists.
- Flight Review or QGroundControl functionality.

## Adoption evidence

The next release is ready for wider promotion only when:

- at least two PX4 release families have redistributable fixture evidence;
- a clean-environment wheel installation and container smoke test pass in CI;
- the example workflow produces a validator-clean dataset;
- privacy limitations and contribution licensing are visible before any log request;
- benchmark tables contain measured results rather than estimates.

## Focused backlog

| Issue | Acceptance evidence |
|---|---|
| Add authorized PX4 release fixtures | Provenance, license, privacy sidecar, expected topic inventory |
| Review release-aware field transforms | Official message definitions and golden output tests |
| Publish the example research dataset | Rebuild command, config digest, checksums, citation and data license |
| Measure the reference corpus | Raw timings, peak RSS, environment, five repetitions, validation result |
| Design contribution bundle preview | No network path; explicit consent and privacy review output |
| Publish manifest JSON Schema | Valid/invalid fixtures and CI validation |
| Add bounded parser resource policy | Hostile-input tests and documented limits |
