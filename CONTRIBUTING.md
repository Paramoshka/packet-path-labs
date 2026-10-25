# Contributing / personal workflow

A useful pattern for extending a lab with Codex:

1. Deploy the existing baseline.
2. Capture the current control/data plane state.
3. Change one thing only.
4. Write the expected result before testing.
5. Save useful commands or captures in the lab README.

Keep lab directories self-contained whenever practical.

For new labs, include topology, prerequisites, a working baseline (or an explicit
intentional failure), expected observations, bounded diagnostic commands and
reset/persistence instructions. Keep data traffic off Docker's management eth0.

Run `make check` before committing. Runtime checks should use a fresh lab and
record both positive and negative cases in `VALIDATION.md`; YAML validation
alone is not evidence that routing or service behavior works. Never reuse or
destroy another learner's running lab for tests.

`MANIFEST.sha256` records repository source files except itself. Refresh it when
source files change; exclude ignored runtime directories and captures.
