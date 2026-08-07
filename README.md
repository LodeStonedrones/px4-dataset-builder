# PX4 Dataset Builder

PX4 Dataset Builder turns one or more PX4 `.ulg` flight logs into versioned, documented datasets for statistics, research, debugging, carefully designed machine-learning workflows, and benchmarking.

It is independent, local-first, and completely open source. It contains no proprietary navigation, anti-jamming, sensor-fusion, control, or commercial decision logic. Event labels are ordinary configurable rules, not ground truth and not flight-safety verdicts.

## Why this exists

ULogs are rich but heterogeneous: uORB fields change across PX4 releases, topics run at different frequencies, real fleets have missing data, and a naive row split leaks samples from the same flight into training and test. PX4 Dataset Builder provides a reproducible boundary between source logs and downstream analysis:

- canonical signal names and units mapped from documented uORB field candidates;
- gap-aware, signal-specific synchronization;
- explicit missing data and quality findings;
- flight/group-level train, validation, and test splits;
- optional coordinate and metadata anonymization;
- CSV, JSON Lines, and compressed Parquet outputs;
- one manifest describing provenance, population, events, failures, and split distribution.

Processing is local. The application makes no network request and never uploads a log.

## Installation

Python 3.12 or newer is required. There is no PyPI release yet; install the current alpha from source:

```bash
git clone https://github.com/LodeStonedrones/px4-dataset-builder.git
cd px4-dataset-builder
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

For development:

```bash
python -m pip install -e '.[dev]'
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

Mappings, units, sensitivity, valid ranges, and interpolation policies live in `topics/catalog.py` and are copied to `metadata/signal_schema.json`. Unknown or unavailable fields are not guessed. The current automated compatibility evidence uses the included synthetic ULog; a public matrix of real PX4 release fixtures is planned for v0.2.

## Event rules

The default YAML demonstrates `gps_lost`, `gps_degraded`, satellite/EPH/EPV checks, estimator reset/warning, vibration, battery levels, failsafe, takeoff, landing, mode change, and sensor gaps. Logged PX4 warning and error messages are extracted separately as timestamped events.

Four rule kinds are supported:

- `threshold`: contiguous interval satisfying a simple comparison;
- `change`: a finite state/counter value changes;
- `edge`: a comparison changes from false to true;
- `gap`: a null interval exceeds a duration.

Every rule-derived event records the rule name, signal, observed value, threshold, interval, severity, and description. Log-message events record their timestamp, severity, and message instead. Overlapping events remain visible—for example, a critical battery interval can also satisfy the broader low-battery rule.

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

Each worker parses, normalizes, validates, and stages one flight at a time. The coordinator retains compact metadata and events while completed flight tables are written to disk instead of retaining the entire dataset in memory. `--workers` enables process-level parallelism for independent logs. Parquet uses Zstandard compression. No 100/1,000-log benchmark has been published yet; that evidence is part of the roadmap.

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

v0.1 is a working alpha validated by unit and end-to-end tests using a deterministic synthetic ULog. It does not yet claim a real-flight PX4 compatibility matrix. It intentionally does not implement ROS 2 bags, HDF5/Arrow IPC, a web dashboard, Hugging Face publishing, Flight Review integration, ArduPilot/MAVLink parsing, cloud execution, or a dataset registry. Those are documented future adapters and will not enter the core until schemas and privacy behavior are stable.

## Relationship to the PX4 ecosystem

The parser is built on [PX4/PyULog](https://github.com/PX4/pyulog). This project focuses on local, synchronized dataset preparation, privacy controls, and flight-level dataset splits. It is complementary to [PX4 Flight Review v2](https://github.com/PX4/flight-review-rs), which provides log conversion, diagnostics, and interactive review.

PX4 Dataset Builder is an independent community project. It is not an official PX4 project and is not affiliated with or endorsed by PX4 or the Dronecode Foundation.

## Contributing and community

Start with [CONTRIBUTING.md](CONTRIBUTING.md), especially the log-data rules. Synthetic fixtures and authorized fixtures that have been carefully reviewed for privacy are particularly valuable. Do not attach sensitive, personal, or operational flight logs to public issues.

The [community strategy](docs/community/STRATEGY.md) proposes a synthetic demo, PX4 Discuss/Discord feedback, useful upstream contributions, ethical log requests, and a possible future transfer to a neutral community organization.

## License

This project is licensed under the [Apache License 2.0](LICENSE). Apache-2.0 is a permissive open-source license that includes an explicit patent license covering applicable contributor patent claims.

The license covers this project. It does not grant rights to use PX4 or other third-party trademarks. PX4 is referenced solely to describe technical compatibility.
