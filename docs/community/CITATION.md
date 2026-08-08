# Research citation guidance

No DOI or immutable archival release has been issued. Do not cite the repository as though one exists.

For reproducible work, record:

- project name: **PX4 Dataset Builder**;
- exact package version reported by `px4-dataset --version`;
- full Git commit SHA;
- repository URL: <https://github.com/LodeStonedrones/px4-dataset-builder>;
- access date;
- configuration and manifest schema version;
- the data license and provenance separately from the software citation.

Suggested interim citation:

> PX4 Dataset Builder contributors. *PX4 Dataset Builder* (version 0.1.0 source, commit `<full SHA>`). GitHub repository, accessed `<YYYY-MM-DD>`. https://github.com/LodeStonedrones/px4-dataset-builder

Use the repository's [`CITATION.cff`](../../CITATION.cff) support where available, but replace or supplement the version with the exact commit used. Once a tagged archival release and DOI exist, this page and `CITATION.cff` should be updated in the same pull request.

The Apache-2.0 software license does not determine how flight logs or generated datasets may be cited or reused. Cite datasets according to their own provenance and license.
