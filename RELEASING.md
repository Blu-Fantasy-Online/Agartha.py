# Release publication

BFO maintainers build the SDK from its private source and run the SDK, API,
database contract, frontend export, and browser checks before publication.
The public repository contains documentation and examples; SDK implementation
files and platform source do not belong in its Git history.

For each validated release, update these guides and examples, then attach the
official wheel, SDK LICENSE, SHA256SUMS, and latest.json to a versioned GitHub
release. Check the downloaded wheel hash against SHA256SUMS and confirm the
wheel metadata contains the proprietary license and current project URLs.

Publish the same wheel and latest.json on the BFO website. Yunai checks the BFO
manifest every five minutes and announces each version once in the configured
Discord news channel. A GitHub draft alone does not trigger that announcement.
Do not overwrite an existing published version; use a new SDK version for fixes.
