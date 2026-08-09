# Contributing PX4 flight data

Real-world PX4 ULogs are valuable for compatibility testing, reproducible research, and
benchmarking. They can also expose locations, people, vehicles, customers, operational
procedures, and confidential engineering work. Treat every ULog as sensitive until its
owner has reviewed and authorized a specific use.

> [!IMPORTANT]
> PX4 Dataset Builder processes files locally. It has no upload button, network client,
> telemetry, or automatic sharing path. You decide whether anything leaves your system.

```text
Original ULog
    → local PX4 Dataset Builder processing
    → sanitized dataset
    → manual preview and rights review
    → explicit decision by the data owner
    → separate, approved sharing process if appropriate
```

## Choose one path

These paths are deliberately separate. A private research relationship is not a public
open-source dataset contribution, and opening a GitHub issue grants no data rights.
This document provides project-operational guidance, not legal advice; each data owner
remains responsible for obtaining appropriate legal and institutional review.

| Path | Intended result | Public? | First contact |
|---|---|---:|---|
| **Community Contribution** | Redistributable fixture, benchmark input, or open research dataset | Yes, after review | [Dataset Contribution issue](https://github.com/LodeStonedrones/px4-dataset-builder/issues/new?template=dataset.yml) |
| **LodeStone Research Partnership** | Time- and purpose-bounded research under a separate written agreement | No, unless separately authorized | [LodeStone's published contact channels](https://github.com/LodeStonedrones) — send no data initially |

## What data is useful

We are especially looking for legally shareable or privately reviewable PX4 ULogs that
improve evidence for:

- PX4 release compatibility and uORB schema changes;
- missing or renamed GPS, IMU, estimator, battery, actuator, or vehicle-status fields;
- multiple sensor/topic instances;
- truncated, incomplete, or irregular logs that are safe to study;
- GNSS degradation, multipath, indoor operation, high vibration, and other challenging
  non-sensitive research conditions;
- different vehicle classes represented at a coarse, non-identifying level;
- reproducible performance and memory benchmarks.

A small, well-documented fixture is usually more useful than a large operational archive.
Synthetic reproductions remain the preferred option when they can exercise the same
format or failure mode.

## What not to send

Do not send or publicly link:

- classified, export-controlled, military, or defense operational data;
- customer-confidential or employer-confidential material;
- accident or active safety-investigation evidence;
- exact sensitive locations, routes, home positions, or takeoff sites;
- personal information, operator names, serial numbers, UUIDs, or customer identifiers;
- proprietary source code, algorithms, thresholds, configurations, or model artifacts;
- any log you do not own or lack authority to use for the proposed purpose.

Do not attach a ULog to an issue, Discussion, pull request, email, or security report unless
a named recipient has confirmed in writing that the specific transfer is authorized and
has provided an appropriate transfer method.

## Review and anonymize locally

First inspect the source locally:

```bash
px4-dataset inspect flight.ulg
```

Create and review an anonymization configuration, then generate a separate dataset:

```bash
px4-dataset init-config --output config.yaml
px4-dataset build flight.ulg --config config.yaml --anonymize --output sanitized-dataset
px4-dataset validate sanitized-dataset
```

Before sharing, manually inspect every generated flight table, metadata file, event,
quality report, effective configuration, and manifest. Check for:

- absolute or recognizable relative trajectories;
- UTC timestamps and filenames;
- UUIDs, hardware and firmware fingerprints;
- free-text warnings and custom event descriptions;
- rare event sequences or configurations that could identify the operation;
- source hashes that could link the result to another copy of the log.

Anonymization reduces exposure; it does not prove anonymity. A sanitized dataset can
remain identifiable through trajectory shape, timing, vehicle configuration, or external
knowledge.

## Community Contribution

Use this path only when the intended artifact may be made public.

1. Open a [Dataset Contribution issue](https://github.com/LodeStonedrones/px4-dataset-builder/issues/new?template=dataset.yml) without attaching or linking data.
2. Describe the PX4 release, non-sensitive scenario, reviewed topic inventory, and the
   compatibility or research question.
3. State who owns or controls the data and who authorized redistribution and derivatives.
4. Propose a separate data license. Apache-2.0 covers the software, not flight logs or
   generated datasets.
5. Agree on minimization, anonymization, provenance, retention, attribution, and the
   exact files that may become public.
6. Transfer anything only after written maintainer instructions.

Accepted public artifacts may be used as versioned compatibility fixtures, reproducible
benchmark inputs, or open research datasets. Acceptance is not guaranteed, and a public
issue does not transfer ownership or grant a license.

## LodeStone Research Partnership

This path is for universities, laboratories, and companies that may authorize a defined
research use but cannot release the underlying data publicly.

It is separate from the open-source contribution process. Before any transfer, the parties
must agree in writing on:

- the data controller and authorized contacts;
- the exact research purpose and permitted analyses;
- whether derived statistics, compatibility findings, or code fixes may be published;
- prohibited uses and onward disclosure;
- minimization and anonymization responsibilities;
- transfer security, storage location, access controls, and incident handling;
- retention period, deletion date, and deletion confirmation;
- attribution, confidentiality, withdrawal, and applicable legal terms.

Private data is not added to this repository, does not become Apache-2.0 data, and is not
used as a permanent public test dependency unless the owner later grants separate written
permission. Contact LodeStone through its [official GitHub profile](https://github.com/LodeStonedrones)
or [website](https://lodestonedrones.com) with a non-sensitive description only. Do not send
the log with the initial message.

## Required provenance for any accepted public fixture

Every public fixture needs a reviewed sidecar recording:

- PX4 release and, where relevant, firmware commit;
- coarse vehicle class and relevant sensors, without unique identifiers;
- ownership, authorization, and data license;
- permitted uses and derivative rights;
- anonymization/minimization steps and residual risks;
- source and sanitized artifact digests under the approved hash policy;
- expected topics, canonical signals, quality findings, and compatibility result;
- responsible contact and review date.

For code and documentation contributions, use [CONTRIBUTING.md](CONTRIBUTING.md). For the
full privacy threat model, read [Privacy and data governance](docs/privacy/PRIVACY.md).
