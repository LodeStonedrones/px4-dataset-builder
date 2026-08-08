# Quick start tutorial

This tutorial creates a complete local dataset from a deterministic synthetic ULog. It does not require or expose real flight data.

## 1. Install the alpha

Python 3.12 or newer and Git are required. There is no PyPI release yet.

```bash
python3.12 -m venv .venv && source .venv/bin/activate
python -m pip install "git+https://github.com/LodeStonedrones/px4-dataset-builder.git"
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`. Windows is not yet part of the automated compatibility matrix.

## 2. Generate and build

```bash
px4-dataset generate-example && px4-dataset build synthetic-flight.ulg
```

The builder writes `dataset/` in the current directory using Parquet and the default 10 Hz resampling policy.

## 3. Validate and inspect

```bash
px4-dataset validate dataset
px4-dataset stats dataset
```

Validation checks the manifest and every referenced artifact. The synthetic dataset contains one five-second flight and exists only to demonstrate the workflow.

## 4. Process your own reviewed logs

```bash
px4-dataset build ./logs --output ./dataset --format parquet --workers 1
```

Before processing operational logs, read [Privacy and data governance](../privacy/PRIVACY.md). Before sharing any output, inspect flight tables, metadata, events, quality findings, the manifest, and source filenames.

## 5. Configure anonymization deliberately

```bash
px4-dataset init-config --output config.yaml
px4-dataset build ./logs --config config.yaml --anonymize
```

The default anonymization policy removes absolute GPS rather than keeping it. Review every policy value. Anonymization is a risk-reduction transformation, not a guarantee that a flight cannot be identified.

## Next steps

- [Dataset examples and interpretation](../examples/README.md)
- [Compatibility matrix](../../README.md#compatibility)
- [Resampling methodology](../methodology/RESAMPLING.md)
- [Contributor onboarding](../community/CONTRIBUTOR_GUIDE.md)
