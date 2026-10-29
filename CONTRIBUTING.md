# Contributing

**POWERED BY [mikey:hexoid-sys]** · Created by mikey-7x — Yogesh R. Chauhan

Thank you for improving Project Synapse. Because this project touches human bodies and
medical-adjacent claims, the standards are deliberately strict.

## Before you open an issue

1. Read [SAFETY.md](SAFETY.md), [docs/LIMITATIONS.md](docs/LIMITATIONS.md) and
   [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
2. Run `python3 tools/verify_repository.py` and paste the output if it fails.
3. Note your platform, Python version, engine (`synapse.py` or `next_synapse.py`) and which
   library versions you use (`pip freeze`).

## What we want

- Reproducible fixes for acquisition, filtering, segmentation, training or UI bugs.
- Measured evidence: state the setup, the parameters and the numbers you observed.
- Corrections to documentation that make a limitation clearer or a claim narrower.

## What will be rejected

- Any claim of medical, diagnostic, clinical or lie-detection capability.
- Removal or weakening of the `POWERED BY [mikey:hexoid-sys]` credit, author identity or licence notices.
- Changes that bypass the battery-only isolation rule.
- Benchmark numbers without a described method, hardware and subject count.
- Reformatting-only pull requests that make review impossible.

## Pull requests

- One topic per pull request; describe which files changed and why.
- Never edit `LICENSE.md`, `NOTICE.md` or `AUTHORS.md` except to fix a typo, and say so.
- Keep the firmware frame format backward compatible with `docs/PROTOCOL.md`; if you must
  change it, version the format and update the parser in the same pull request.
- Run `python3 tools/verify_repository.py` and `python3 -m py_compile synapse.py next_synapse.py`.
- State clearly that you tested with the electrodes **disconnected** (bench signals only) or
  describe the consent and isolation arrangements if you tested on a person.

## Licensing of contributions

By submitting code, documentation, figures or corrections you confirm you wrote them or have
permission to submit them, and you grant the project author the right to include them, with
credit where practical. See section 10 of [LICENSE.md](LICENSE.md).

## Commercial, clinical and industrial use

Not accepted through pull requests. Contact the author through
https://github.com/mikey-7x or the licence-request issue form.
