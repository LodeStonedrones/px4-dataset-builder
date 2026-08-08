# Benchmarks and compatibility evidence

## Current status

No public performance benchmark over real PX4 flight logs has been published. The tables below define what is known now and the evidence required before performance or release-compatibility claims are added.

## Dataset statistics

The deterministic fixture is functional test evidence, not a representative performance corpus.

| Dataset | Flights | Source topics | Source duration | Normalized rows | Data classification | Purpose |
|---|---:|---:|---:|---:|---|---|
| Built-in synthetic ULog | 1 | 11 | 5 s | 51 at 10 Hz | Synthetic, non-operational | Parser, event, anonymization, exporter, and CLI integration tests |
| Public PX4 release fixture corpus | — | — | — | — | **Not yet collected** | Planned release compatibility |
| Public scale corpus | — | — | — | — | **Not yet collected** | Planned throughput and peak-memory measurements |

Do not fill unknown cells with estimates. A fixture row must link to its provenance, license, redaction statement, input digest policy, and expected topic inventory.

## Compatibility matrix

The user-facing matrix is maintained in the [README](../README.md#compatibility). A row may be marked **Validated** only when a redistributable or CI-accessible fixture exercises the documented path and a regression test records the expected schema or behavior.

Compatibility evidence should record:

- PX4 release and, when relevant, message-format or firmware commit;
- vehicle class at a non-identifying level;
- fixture provenance and redistribution permission;
- source topic and field inventory;
- canonical signals produced and intentionally unavailable signals;
- warnings, conversion losses, and quality findings;
- operating system, architecture, Python version, and dependency lock;
- exact builder commit and configuration.

## Performance measurement protocol

Measure end-to-end behavior from a clean output directory. Include parsing, normalization, event detection, privacy transformation, splitting, export, and report generation.

For every result:

1. use public, synthetic, or authorized reproducible inputs;
2. record the exact Git commit and a dependency lock or container digest;
3. publish the complete configuration and command;
4. record CPU, memory, storage type, operating system, Python version, worker count, and output format;
5. separate cold-cache and warm-cache runs when caching can affect results;
6. run at least five measured repetitions after one warm-up;
7. report median, minimum, maximum, and a percentile or dispersion measure;
8. measure peak resident memory with a documented tool;
9. validate the generated dataset after every run;
10. retain raw measurement output alongside the summarized table.

Suggested result schema:

| Commit | Corpus | Flights | Input size | Duration | Format | Workers | Median wall time | Peak RSS | Result artifact |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| _No reviewed result yet_ | — | — | — | — | — | — | — | — | — |

## Known limitations

- The synthetic fixture is small and does not model full real-flight topic diversity.
- PX4 v1.14–v1.16 real-flight compatibility is planned rather than validated.
- CI confirms correctness on small inputs; it does not establish fleet-scale throughput.
- Peak memory, worker scaling, filesystem sensitivity, and Parquet compression trade-offs have not been published.
- macOS and Windows are not part of the automated compatibility matrix.
- Event thresholds are example policies, not universal vehicle or safety limits.
- Anonymization cannot prove that a trajectory is anonymous.

## Reproducibility checklist

- [ ] Input is public/synthetic or has explicit authorization and documented terms.
- [ ] Repository commit and source version are recorded.
- [ ] Python and dependency versions are captured.
- [ ] Hardware, OS, architecture, and filesystem are described.
- [ ] Configuration and exact command are included.
- [ ] Input identity uses an approved digest policy without leaking sensitive names.
- [ ] Output passes `px4-dataset validate`.
- [ ] Raw measurements and aggregation method are available.
- [ ] Compatibility and performance claims are limited to the measured corpus.

Benchmark contributions should begin with a Discussion or feature proposal so corpus licensing and methodology can be reviewed before large artifacts are added.
