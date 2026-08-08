# Privacy and data governance

ULogs can reveal exact coordinates, UTC time, routes, mission states, vehicle UUIDs, hardware, firmware branches, free-text warnings, filenames, failures, and experimental procedures. Treat every log as sensitive until reviewed.

The project never uploads data. Anonymization can remove absolute coordinates, create local coordinates, remove original timestamps, hash names, remove selected metadata, and redact free text. It is a transformation, not a guarantee: trajectory shape, rare configuration, duration, event sequence, and source hashes can still enable linkage.

The generated provenance includes the effective configuration. Custom rule names and descriptions are therefore publishable dataset content: do not place customer names, mission identifiers, internal thresholds, or other confidential text in a configuration intended for redistribution.

Before sharing a dataset:

1. confirm that the owner/operator authorizes the intended use and redistribution;
2. use a copy and enable the required anonymization policy;
3. inspect flight tables, metadata, events, quality report, and manifest manually;
4. consider removing hashes, uncommon configuration, and rare event descriptions;
5. document the policy/version applied and residual risks;
6. use a data license or agreement distinct from the software license.

Public project fixtures must be synthetic or have explicit redistribution permission and a provenance/redaction statement. Do not request or submit classified, export-controlled, customer-confidential, safety-investigation, military, or operationally sensitive logs.

The default `/dataset/` output and common binary/tabular exports are ignored by Git, but a custom output directory or JSON metadata may not be. Always inspect `git status` before staging changes, and never use `git add --force` for generated flight data without an explicit review.

Commercial or employer code, thresholds, datasets, model artifacts, and internal documentation are out of scope. Contributions must be derived from public PX4 specifications and contributor-owned work.
