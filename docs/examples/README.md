# Examples

Examples must be copyable, deterministic, and safe to publish. Use the built-in synthetic ULog unless a reviewed fixture has explicit redistribution terms.

## Inspect a log without writing a dataset

```bash
px4-dataset inspect synthetic-flight.ulg
```

The command prints metadata, quality findings, event count, and normalized sample count. It does not create a dataset.

## Print configured events

```bash
px4-dataset events synthetic-flight.ulg
```

Events are observations produced by configured threshold, change, edge, and gap rules. They are not automatic safety or anomaly ground truth.

## Choose an output format

```bash
px4-dataset build synthetic-flight.ulg --output dataset-csv --format csv
px4-dataset build synthetic-flight.ulg --output dataset-json --format json
px4-dataset build synthetic-flight.ulg --output dataset-parquet --format parquet
```

The `json` CLI value produces JSON Lines tabular files. Manifests, metadata, statistics, and quality reports remain ordinary JSON documents.

## Build multiple flights

```bash
px4-dataset build ./logs --output ./dataset --workers 4
```

Discovery is recursive. Each successfully processed log remains a complete flight and is assigned to exactly one dataset split. Failures appear in the manifest instead of being silently discarded.

## Example-review checklist

- Use no real coordinates, identifiers, customer text, or personal filesystem paths.
- State whether the input is synthetic or authorized.
- Include the builder version, configuration, and expected output.
- Avoid implying release compatibility that the fixture does not prove.
- Link methodology when an example changes synchronization, splitting, or privacy behavior.
