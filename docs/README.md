# Documentation

This documentation separates user workflows, research methodology, privacy policy, architecture, evidence, and community governance so readers can find the applicable contract without reading the whole repository.

## Start here

| Need | Document |
|---|---|
| Build a first synthetic dataset | [Quick start](tutorials/QUICKSTART.md) |
| Understand outputs and current support | [README compatibility matrix](../README.md#compatibility) |
| Understand module boundaries | [Architecture](architecture/ARCHITECTURE.md) |
| Design a scientifically defensible resampling policy | [Resampling methodology](methodology/RESAMPLING.md) |
| Review privacy before using or sharing logs | [Privacy and data governance](privacy/PRIVACY.md) |
| Reproduce or contribute measurements | [Benchmarks and evidence](benchmarks.md) |
| Contribute code, documentation, or data | [Contributor onboarding](community/CONTRIBUTOR_GUIDE.md) |
| Understand decisions and maintainer roles | [Project governance](community/GOVERNANCE.md) |
| Understand scope and non-goals | [Requirements](REQUIREMENTS.md) |
| See release exit criteria | [Roadmap](ROADMAP.md) |

## Documentation structure

```text
docs/
├── README.md                    # this navigation page
├── REQUIREMENTS.md              # scope, requirements, and non-goals
├── ROADMAP.md                   # milestone exit criteria
├── benchmarks.md                # evidence and reproducibility protocol
├── architecture/                # module boundaries and flows
├── tutorials/                   # task-oriented user walkthroughs
├── examples/                    # reviewed commands and output explanations
├── methodology/                 # scientific transformation decisions
├── privacy/                     # privacy and data-governance policy
├── community/                   # contribution, recognition, and outreach
└── assets/                      # reviewed screenshots and visual assets
```

Benchmark scripts and immutable result artifacts should eventually live in a top-level `benchmarks/` directory, separate from the explanatory `docs/benchmarks.md`. Do not create result files until a public input corpus, environment lock, and reviewable measurement protocol exist.

## Documentation rules

- Distinguish implemented, experimental, and planned behavior.
- Link technical claims to code, tests, public PX4 documentation, or reproducible evidence.
- Never publish private logs, exact operational locations, identifiers, or user-specific paths in examples.
- Use synthetic examples unless a fixture has explicit redistribution permission and a provenance sidecar.
- Update the compatibility table and changelog in the same pull request as compatibility evidence.
- Keep screenshots secondary to copyable commands and machine-readable output.

Documentation problems can be reported with the [Documentation issue form](https://github.com/LodeStonedrones/px4-dataset-builder/issues/new?template=documentation.yml).
