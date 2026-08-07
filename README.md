# PX4 Dataset Builder

PX4 Dataset Builder turns one or thousands of PX4 `.ulg` flight logs into versioned, documented datasets for statistics, machine-learning infrastructure, research, debugging, anomaly-detection experiments, and benchmarking.

It is independent, local-first, and completely open source. It contains no proprietary navigation, anti-jamming, sensor-fusion, control, or commercial decision logic. Event labels are ordinary configurable rules, not ground truth and not flight-safety verdicts.

## Why this exists

ULogs are rich but heterogeneous: uORB fields change across PX4 releases, topics run at different frequencies, real fleets have missing data, and a naive row split leaks samples from the same flight into training and test. PX4 Dataset Builder provides a reproducible boundary between source logs and downstream analysis:

- version-tolerant canonical signal names and units;
- gap-aware, signal-specific synchronization;
- explicit missing data and quality findings;
- flight/group-level train, validation, and test splits;
- optional coordinate and metadata anonymization;
- CSV, JSON Lines, and compressed Parquet outputs;
- one manifest describing provenance, population, events, failures, and split distribution.

Processing is local. The application makes no network request and never uploads a log.

## Installation

Python 3.12 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install px4-dataset-builder
```

For development:

```bash
git clone https://github.com/LodeStonedrones/px4-dataset-builder.git
cd px4-dataset-builder
pip install -e '.[dev]'
make check
```

## Quick start

Generate a small synthetic ULog, inspect it, and build a dataset:

```bash
px4-dataset generate-example --output synthetic.ulg
px4-dataset inspect synthetic.ulg
px4-dataset events synthetic.ulg
px4-dataset build synthetic.ulg --output dataset
px4-dataset validate dataset
px4-dataset stats dataset
```

Build a directory recursively with four worker processes:

```bash
px4-dataset build ./logs \
  --output ./dataset \
  --format parquet \
  --workers 4
```

Enable the anonymization policy from the configuration:

```bash
px4-dataset init-config --output config.yaml
px4-dataset build ./logs --config config.yaml --anonymize
```

Review the generated `config.yaml` before processing operational logs. Default thresholds are examples for transparent triage and may not be appropriate for a vehicle or experiment.

## Dataset layout

```text
dataset/
├── train/flights/             # complete flights assigned to training
├── validation/flights/        # complete flights assigned to validation
├── test/flights/              # complete flights assigned to test
├── flights/index.json         # flight → split/data/metadata mapping
├── events/events.parquet      # or .csv/.jsonl
├── metadata/
│   ├── <flight_id>.json
│   └── signal_schema.json
├── statistics/summary.json
├── data_quality_report.json
└── manifest.json
```

Each flight table is wide and ordered by `time_s`. `timestamp_us` retains the original ULog clock unless anonymization is enabled. A signal appears only when a documented uORB candidate exists. Missing intervals remain null when a gap exceeds `max_interpolation_gap_s`.

The global manifest contains flight/sample counts, total duration, available sensor families, PX4 versions, event and split distributions, failed logs, quality summary, anonymization settings, and resampling policy.

## Canonical signals

The v0.1 catalog covers:

- GPS position, altitude, NED velocity, heading, fix type, satellite count, EPH, and EPV;
- local position and velocity;
- quaternion attitude plus derived roll, pitch, and yaw;
- accelerometer, gyro, magnetometer, and barometer;
- voltage, current, remaining fraction, discharged capacity, and battery warning;
- actuator outputs, navigation mode, arming state, failsafe, land state, and mission sequence;
- public estimator flags, reset counters, test ratios, and selected innovations;
- acceleration and gyro vibration metrics.

Mappings, units, sensitivity, valid ranges, and interpolation policies live in `topics/catalog.py` and are copied to `metadata/signal_schema.json`. Unknown or unavailable fields are not guessed.

## Event rules

The default YAML demonstrates `gps_lost`, `gps_degraded`, satellite/EPh/EPV checks, estimator reset/warning, vibration, battery levels, failsafe, takeoff, landing, mode change, sensor gaps, and PX4 warning/error messages.

Four rule kinds are supported:

- `threshold`: contiguous interval satisfying a simple comparison;
- `change`: a finite state/counter value changes;
- `edge`: a comparison changes from false to true;
- `gap`: a null interval exceeds a duration.

Every event records the rule, signal, observed value, threshold, interval, severity, and human-readable description. Overlapping events remain visible—for example, a critical battery interval can also satisfy the broader low-battery rule.

## Resampling decisions

PX4 topics are asynchronous. The builder creates a regular flight-relative grid, 10 Hz by default:

- continuous quantities use linear interpolation only when surrounding samples are no farther apart than the configured maximum gap;
- modes, flags, counters, and booleans use bounded previous-value semantics;
- quaternions and headings use bounded nearest samples rather than component/angle averaging;
- no extrapolation occurs beyond the maximum gap;
- derived Euler angles are calculated from normalized quaternions.

These choices are defaults, not universal scientific truth. See [Resampling and methodology](docs/RESAMPLING.md) before publishing results.

## Splits and leakage

All samples from one flight stay in exactly one split. Strategies are:

- `random`: seeded flight-level shuffle;
- `flight`: stable identifier hash;
- `drone`: all flights with the same logged UUID stay together;
- `date`: all flights from one UTC date stay together when UTC is available;
- `event`: flight-level stratification by complete event-name signature.

Unknown drone/date groups remain isolated per flight instead of being silently collapsed. For rigorous experiments, choose the group that represents the real generalization boundary and audit `flights/index.json`.

## Privacy

Anonymization is opt-in because modifying evidence must be deliberate. Available policies remove absolute GPS, derive local north/east/relative altitude, remove original timestamps, hash source names, remove vehicle identity, filter selected metadata keys, and redact free-text PX4 warnings.

Anonymization reduces exposure; it cannot guarantee anonymity. Motion patterns, timing, vehicle configuration, rare events, or a known source hash can still identify a flight. Preview output and obtain permission before sharing. See [Privacy and data governance](docs/PRIVACY.md).

## Performance

Each worker parses, normalizes, validates, and stages one flight at a time. The coordinator retains compact metadata/events while flight tables are written immediately, so thousands of logs are not held in RAM together. `--workers` enables process-level parallelism for independent logs. Parquet uses Zstandard compression.

Pandas is used in v0.1 because PyULog already exposes NumPy arrays and Pandas provides mature time-series and export behavior. Polars would help lazy scans and cohort aggregation after files are written, but adding it to the extraction path now would duplicate dataframe dependencies without a measured benefit. A Polars/DuckDB benchmark is planned before adopting either in the core.

## Docker

```bash
docker build -t px4-dataset-builder .
docker run --rm \
  -v "$PWD/logs:/logs:ro" \
  -v "$PWD/dataset:/output" \
  px4-dataset-builder build /logs --output /output
```

The runtime is non-root and has no cloud configuration.

## Architecture and project status

The modular pipeline keeps parsing, normalization, synchronization, event detection, quality, anonymization, splitting, statistics, and export independent. See [Architecture](docs/architecture/ARCHITECTURE.md), [requirements analysis](docs/REQUIREMENTS.md), and the [roadmap](docs/ROADMAP.md).

v0.1 is a working alpha. It intentionally does not implement ROS 2 bags, HDF5/Arrow IPC, a web dashboard, Hugging Face publishing, Flight Review integration, ArduPilot/MAVLink parsing, cloud execution, or a dataset registry. Those are documented future adapters and will not enter the core until schemas and privacy behavior are stable.

## Contributing and community

Start with [CONTRIBUTING.md](CONTRIBUTING.md), especially the log-data rules. Synthetic fixtures and authorized, meaningfully anonymized compatibility fixtures are valuable. Do not attach sensitive or operational logs to public issues.

The [community strategy](docs/community/STRATEGY.md) proposes a neutral GitHub launch, a synthetic demo, PX4 Discuss/Discord feedback, useful upstream contributions, and ethical log requests.

## License choice

Apache-2.0 was selected over MIT and BSD-3-Clause because all three are permissive, while Apache-2.0 also provides an explicit patent grant and contribution patent terms that are useful for collaboration among universities, individuals, and companies. It does not make PX4 trademarks part of this project. See [LICENSE](LICENSE).
