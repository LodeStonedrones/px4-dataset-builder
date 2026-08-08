# Resampling and methodology

## Default time base

Every source topic keeps its ULog microsecond timestamp during parsing. Normalization converts it to `time_s = (timestamp - ulog_start) / 1e6`. A regular grid spans zero through the recorded duration at `frequency_hz`.

## Policies

`linear` requires two surrounding finite samples and refuses to bridge an interval larger than `max_interpolation_gap_s`. `previous` carries a state only for that same bounded duration. `nearest` selects a real observation within the bound. `none` accepts an exact match only.

The generated grid never extends past the logged flight duration. `max_output_rows`
(1,000,000 by default) rejects configurations or hostile timestamps that would otherwise
allocate an unexpectedly large normalized table; it can be adjusted explicitly for trusted,
high-rate datasets.

Quaternion components use nearest observation, then are normalized before public quaternion-to-Euler equations produce roll, pitch, and yaw. Heading uses nearest observation because interpolation across the ±π discontinuity is misleading. Modes, counters, flags, booleans, and actuator output representation use previous-value behavior. GPS and ordinary translational measurements use bounded linear interpolation.

## Scientific cautions

- Choose a target frequency no higher than the lowest meaningful source rate for the downstream question.
- Null intervals are evidence of unavailability; do not automatically fill them later.
- Nearest quaternion sampling is conservative but does not provide uniform-rate rotational interpolation. Add an explicitly reviewed SLERP policy if a study requires it.
- Coordinate anonymization uses a local equirectangular approximation suitable for short displacement visualization, not navigation or geodesy.
- Event duration is measured on the normalized grid and is therefore quantized by its period.
- Compare manifests and signal schemas before merging independently built datasets.

The project reports transformation choices; researchers remain responsible for validating them against their experimental design.
