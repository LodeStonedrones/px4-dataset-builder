# GitHub Discussions

Discussions should support design and research exchange without becoming an unsafe file-transfer channel or an unstructured support queue.

## Recommended categories

| Category | Purpose | Moderation note |
|---|---|---|
| **General** | Project-wide conversation and community coordination | Redirect support and design threads to a more specific category |
| **Research** | Methodology, reproducibility, papers, and experimental design | Require assumptions and public references; no unsupported performance claims |
| **Datasets** | Dataset schemas, manifests, licensing, and public corpus design | Discuss metadata first; do not upload unreviewed datasets |
| **Flight Logs** | Coordinate synthetic, local-inventory, or authorized-fixture contributions | Never attach sensitive or operational ULogs publicly |
| **Questions** | Installation, CLI, formats, and interpretation | Configure as Q&A so accepted answers remain discoverable |
| **Ideas** | Early proposals that are not ready for an issue | Move bounded, accepted work to an issue |
| **Showcase** | Public tools, papers, and reproducible workflows using the project | Require disclosure of data source, version, and limitations |

Keep **Announcements** as a maintainer-only category for releases, compatibility changes, and governance notices. Polls are optional and should not decide technical or privacy policy without written rationale.

## Current-to-recommended mapping

- keep `General`, `Ideas`, and `Announcements`;
- rename `Q&A` to `Questions` if GitHub permits while retaining the Q&A format;
- rename `Show and tell` to `Showcase`;
- add `Research`, `Datasets`, and `Flight Logs`;
- archive or retain `Polls` only if maintainers plan to use it.

## Pinned guidance

Pin a welcome post that links the compatibility matrix, contributor guide, privacy policy, roadmap, and issue forms. State prominently that opening a Discussion does not authorize public or private log transfer.

Moderators should remove exposed coordinates or identifiers promptly, preserve only the minimum incident record required, and move security-sensitive reports to [Private Vulnerability Reporting](https://github.com/LodeStonedrones/px4-dataset-builder/security/advisories/new).
