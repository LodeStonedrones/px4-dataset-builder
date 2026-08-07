# Community adoption strategy

## Repository and name

The initial repository is hosted at `LodeStonedrones/px4-dataset-builder`. Keep its presentation independent of commercial products and avoid claims of official PX4 status. If external maintainers join, consider transferring it to a neutral community organization. Check name and trademark expectations with PX4 maintainers as community adoption grows.

The initial launch includes a quick start, synthetic demo, CI, privacy policy, issue templates, and an explicit alpha label. Before wider promotion, validate the documented workflow from a clean Python 3.12 environment and publish bounded starter issues. Continue to distinguish implemented features from roadmap items.

## Demo and sample data

The first demo should use `px4-dataset generate-example`, show inspect/events/build/validate, open the manifest and Parquet schema, then rebuild with relative-coordinate anonymization. It demonstrates the full workflow without exposing a real site or vehicle.

Add real-version compatibility fixtures only when redistribution is explicit. Every fixture needs a sidecar with contributor, PX4 version, vehicle class at a coarse level, consent/license, redaction, and permitted use. Synthetic data remains the mandatory CI baseline.

## PX4 channels

1. Open a concise [PX4 Discuss](https://discuss.px4.io/) post: problem, 90-second demo, architecture/non-goals, current compatibility, and two concrete review questions.
2. Share the Discuss link—not a duplicate sales pitch—in the relevant [PX4 Discord](https://discord.gg/BDYmr6FA6Q) development channel.
3. Attend the [weekly PX4 Community Q&A call](https://docs.px4.io/main/en/contribute/dev_call.html) before requesting a slot. Ask for 5–7 minutes only after feedback produces a real revision.
4. Position the tool as a local dataset pipeline complementary to Flight Review, not a replacement.
5. Follow up with public notes, decisions, and issues.

Useful upstream contributions build trust: PyULog parser bugs with minimal reproductions, public uORB mapping documentation, PX4-version fixture metadata, Flight Review export-schema discussion, and ROS 2 message compatibility tests. Avoid asking upstream to own the project before it has external maintainers.

## Feedback and pull requests

- Enable Discussions for signal-schema and methodology proposals.
- Use issue forms that ask for PX4 release, topic inventory, expected mapping, privacy status, and whether a synthetic reproduction is possible.
- Label real, bounded first contributions: one field mapping, one quality assertion, one docs example, one compatibility fixture.
- Publish architecture decisions for schema, resampling, privacy, and format loss.
- Respond within a stated service goal and say honestly when maintainers lack capacity.
- Credit code, reviews, fixtures, research methodology, and documentation in releases.

## Ethical log contribution paths

Never incentivize classified, commercially confidential, customer, military, accident-investigation, or operationally sensitive logs. Offer three paths:

1. **Synthetic reproduction:** preferred; contributor generates or minimizes a non-operational ULog.
2. **Local inventory:** contributor runs `inspect` and shares only reviewed topic/schema/quality output.
3. **Authorized fixture:** explicit redistribution and research use, redaction preview, provenance sidecar, manual approval.

For a private parser investigation, use named maintainers, encrypted transfer, a written purpose and deletion date, no cloud upload, no long-term test dependency, and deletion confirmation. Do not promise anonymity; describe transformations and residual linkage risks.

Universities and laboratories should have a short contribution agreement covering ownership, authorization, purpose, retention, redistribution, withdrawal before release, attribution preference, and responsible contact. Companies should generate a deliberately releasable test log rather than sanitize an operational archive when possible.

## Adoption measures

- clean-install success rate and time to first dataset;
- PX4 versions covered by authorized fixtures;
- external contributors and repeat contributors;
- downstream papers/tools that cite a manifest/schema version;
- parser/schema bugs resolved upstream;
- privacy incidents and unauthorized data: target zero.
